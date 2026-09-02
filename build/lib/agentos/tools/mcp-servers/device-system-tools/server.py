#!/usr/bin/env python3
"""
Device System Tools — MCP Server (Stdio Transport)

Exposes Android device monitoring and management capabilities:
battery, thermals, CPU, memory, storage, and process management.
Reads from /proc and /sys virtual filesystems.

Transport: stdio (JSON-RPC over stdin/stdout)
Platform: Android Termux (also works on standard Linux)
"""

import json
import logging
import os
import re
import signal
import subprocess
import time
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

POWER_SUPPLY_PATH = Path("/sys/class/power_supply")
THERMAL_PATH = Path("/sys/class/thermal")
PROC_STAT = Path("/proc/stat")
PROC_MEMINFO = Path("/proc/meminfo")
PROC_LOADAVG = Path("/proc/loadavg")

# Critical PIDs that must never be killed
PROTECTED_PIDS = {1}  # PID 1 is init
PROTECTED_NAMES = {"zygote", "zygote64", "system_server", "surfaceflinger", "servicemanager", "init"}
ALLOWED_SIGNALS = {signal.SIGTERM, signal.SIGKILL}  # 15, 9

logger = logging.getLogger("device-tools")
logger.setLevel(logging.DEBUG)

# ---------------------------------------------------------------------------
# MCP Server
# ---------------------------------------------------------------------------

mcp = FastMCP(
    "device-system-tools",
    description=(
        "Device monitoring and management tools. Check battery, thermals, "
        "CPU, memory, storage, and processes. Designed for Android Termux "
        "but also works on standard Linux systems."
    ),
)


# ---------------------------------------------------------------------------
# Internal Helpers
# ---------------------------------------------------------------------------

def _read_sys_file(path: Path) -> str | None:
    """Safely read a sysfs/procfs file."""
    try:
        return path.read_text().strip()
    except (FileNotFoundError, PermissionError, OSError):
        return None


def _parse_meminfo() -> dict[str, int]:
    """Parse /proc/meminfo into a dict of values in kB."""
    result = {}
    content = _read_sys_file(PROC_MEMINFO)
    if not content:
        return result
    for line in content.splitlines():
        match = re.match(r"^(\w+):\s+(\d+)", line)
        if match:
            result[match.group(1)] = int(match.group(2))
    return result


def _parse_cpu_stat() -> list[list[int]]:
    """Parse /proc/stat and return per-CPU tick arrays."""
    content = _read_sys_file(PROC_STAT)
    if not content:
        return []
    cpus = []
    for line in content.splitlines():
        if line.startswith("cpu") and line[3:4].isdigit():
            parts = line.split()
            ticks = [int(x) for x in parts[1:]]
            cpus.append(ticks)
    return cpus


def _find_power_supply(supply_type: str = "Battery") -> Path | None:
    """Find the power supply directory matching a type."""
    if not POWER_SUPPLY_PATH.exists():
        return None
    for entry in POWER_SUPPLY_PATH.iterdir():
        type_file = entry / "type"
        stype = _read_sys_file(type_file)
        if stype and stype.lower() == supply_type.lower():
            return entry
    # Fallback: try common names
    for name in ("battery", "Battery", "BAT0", "BAT1"):
        candidate = POWER_SUPPLY_PATH / name
        if candidate.exists():
            return candidate
    return None


# ---------------------------------------------------------------------------
# Tools — Battery
# ---------------------------------------------------------------------------

@mcp.tool()
def battery_status() -> dict:
    """
    Get current battery information: level, charging state, health,
    temperature, voltage, and technology.
    Reads from /sys/class/power_supply/.
    """
    bat = _find_power_supply("Battery")
    if not bat:
        return {"error": "no_battery", "detail": "No battery power supply found in sysfs"}

    def read(name: str) -> str | None:
        return _read_sys_file(bat / name)

    temp_raw = read("temp")
    temp_c = round(int(temp_raw) / 10, 1) if temp_raw and temp_raw.isdigit() else None

    voltage_raw = read("voltage_now")
    voltage_v = round(int(voltage_raw) / 1_000_000, 2) if voltage_raw and voltage_raw.isdigit() else None

    current_raw = read("current_now")
    current_ma = round(int(current_raw) / 1000, 1) if current_raw else None

    return {
        "level_percent": int(read("capacity") or -1),
        "status": read("status"),  # Charging, Discharging, Full, Not charging
        "health": read("health"),
        "temperature_c": temp_c,
        "voltage_v": voltage_v,
        "current_ma": current_ma,
        "technology": read("technology"),
        "charge_full": read("charge_full"),
        "charge_now": read("charge_now"),
    }


# ---------------------------------------------------------------------------
# Tools — Thermal
# ---------------------------------------------------------------------------

@mcp.tool()
def thermal_status() -> dict:
    """
    Read all thermal zone temperatures from /sys/class/thermal/.
    Returns each zone's name, type, and temperature in Celsius.
    Useful for checking if the device is thermally throttling.
    """
    if not THERMAL_PATH.exists():
        return {"error": "no_thermal_data", "zones": []}

    zones = []
    for entry in sorted(THERMAL_PATH.iterdir()):
        if not entry.name.startswith("thermal_zone"):
            continue
        temp_raw = _read_sys_file(entry / "temp")
        zone_type = _read_sys_file(entry / "type") or entry.name

        temp_c = None
        if temp_raw and temp_raw.lstrip("-").isdigit():
            raw_int = int(temp_raw)
            # Values > 1000 are in millidegrees
            temp_c = round(raw_int / 1000, 1) if abs(raw_int) > 200 else float(raw_int)

        zones.append({
            "zone": entry.name,
            "type": zone_type,
            "temperature_c": temp_c,
        })

    hottest = max(zones, key=lambda z: z["temperature_c"] or 0) if zones else None

    return {
        "zone_count": len(zones),
        "zones": zones,
        "hottest": hottest,
        "throttling_warning": hottest and hottest["temperature_c"] and hottest["temperature_c"] > 70,
    }


# ---------------------------------------------------------------------------
# Tools — CPU
# ---------------------------------------------------------------------------

@mcp.tool()
def cpu_usage(interval_ms: int = 500) -> dict:
    """
    Measure CPU utilization by sampling /proc/stat twice.
    Returns per-core and aggregate usage percentages.

    Args:
        interval_ms: Milliseconds between samples (default 500).
    """
    interval_ms = max(100, min(interval_ms, 5000))

    snap1 = _parse_cpu_stat()
    time.sleep(interval_ms / 1000.0)
    snap2 = _parse_cpu_stat()

    if not snap1 or not snap2 or len(snap1) != len(snap2):
        return {"error": "cpu_stat_unavailable"}

    cores = []
    total_usage = 0.0

    for i, (s1, s2) in enumerate(zip(snap1, snap2)):
        # Ticks: user, nice, system, idle, iowait, irq, softirq, steal
        idle1 = s1[3] + (s1[4] if len(s1) > 4 else 0)
        idle2 = s2[3] + (s2[4] if len(s2) > 4 else 0)
        total1 = sum(s1)
        total2 = sum(s2)

        total_delta = total2 - total1
        idle_delta = idle2 - idle1

        if total_delta > 0:
            usage = round((1 - idle_delta / total_delta) * 100, 1)
        else:
            usage = 0.0

        cores.append({"core": i, "usage_percent": usage})
        total_usage += usage

    aggregate = round(total_usage / len(cores), 1) if cores else 0.0

    # Load average
    loadavg_raw = _read_sys_file(PROC_LOADAVG)
    load_1, load_5, load_15 = None, None, None
    if loadavg_raw:
        parts = loadavg_raw.split()
        load_1, load_5, load_15 = float(parts[0]), float(parts[1]), float(parts[2])

    return {
        "core_count": len(cores),
        "cores": cores,
        "aggregate_percent": aggregate,
        "load_average_1m": load_1,
        "load_average_5m": load_5,
        "load_average_15m": load_15,
        "sample_interval_ms": interval_ms,
    }


# ---------------------------------------------------------------------------
# Tools — Memory
# ---------------------------------------------------------------------------

@mcp.tool()
def memory_usage() -> dict:
    """
    Get RAM and swap usage from /proc/meminfo.
    Returns total, used, available, and swap statistics in MB.
    """
    info = _parse_meminfo()
    if not info:
        return {"error": "meminfo_unavailable"}

    total = info.get("MemTotal", 0)
    available = info.get("MemAvailable", 0)
    free = info.get("MemFree", 0)
    buffers = info.get("Buffers", 0)
    cached = info.get("Cached", 0)
    swap_total = info.get("SwapTotal", 0)
    swap_free = info.get("SwapFree", 0)

    used = total - available if available else total - free - buffers - cached

    return {
        "total_mb": round(total / 1024, 1),
        "used_mb": round(used / 1024, 1),
        "available_mb": round(available / 1024, 1),
        "free_mb": round(free / 1024, 1),
        "buffers_mb": round(buffers / 1024, 1),
        "cached_mb": round(cached / 1024, 1),
        "swap_total_mb": round(swap_total / 1024, 1),
        "swap_used_mb": round((swap_total - swap_free) / 1024, 1),
        "swap_free_mb": round(swap_free / 1024, 1),
        "usage_percent": round(used / total * 100, 1) if total else 0,
    }


# ---------------------------------------------------------------------------
# Tools — Storage
# ---------------------------------------------------------------------------

@mcp.tool()
def storage_info() -> dict:
    """
    Get filesystem usage for key partitions.
    Returns total, used, and available space in GB for each mount point.
    """
    mount_points = [
        "/data",
        "/storage/emulated/0",
        os.path.expanduser("~"),
    ]

    partitions = []
    seen_devices = set()

    for mount in mount_points:
        try:
            stat = os.statvfs(mount)
            # Use f_fsid to deduplicate same filesystem
            total = stat.f_blocks * stat.f_frsize
            avail = stat.f_bavail * stat.f_frsize
            used = total - (stat.f_bfree * stat.f_frsize)

            partitions.append({
                "mount": mount,
                "total_gb": round(total / (1024 ** 3), 2),
                "used_gb": round(used / (1024 ** 3), 2),
                "available_gb": round(avail / (1024 ** 3), 2),
                "usage_percent": round(used / total * 100, 1) if total else 0,
            })
        except (OSError, FileNotFoundError):
            partitions.append({
                "mount": mount,
                "error": "inaccessible",
            })

    return {"partitions": partitions}


# ---------------------------------------------------------------------------
# Tools — Processes
# ---------------------------------------------------------------------------

@mcp.tool()
def process_list(sort_by: str = "cpu", limit: int = 10) -> dict:
    """
    List the top N processes sorted by CPU or memory usage.
    Reads from /proc/[pid]/ virtual filesystem.

    Args:
        sort_by: Sort criteria — 'cpu' or 'mem' (default 'cpu').
        limit: Number of processes to return (default 10, max 50).
    """
    limit = max(1, min(limit, 50))
    processes = []

    proc_path = Path("/proc")
    hz = os.sysconf("SC_CLK_TCK")

    for entry in proc_path.iterdir():
        if not entry.name.isdigit():
            continue
        pid = int(entry.name)
        try:
            # Read comm (process name)
            comm = _read_sys_file(entry / "comm") or "?"

            # Read stat for CPU ticks
            stat_raw = _read_sys_file(entry / "stat")
            if not stat_raw:
                continue
            stat_parts = stat_raw.split()
            utime = int(stat_parts[13])
            stime = int(stat_parts[14])
            total_ticks = utime + stime

            # Read status for memory
            rss_kb = 0
            status_raw = _read_sys_file(entry / "status")
            if status_raw:
                for line in status_raw.splitlines():
                    if line.startswith("VmRSS:"):
                        rss_kb = int(line.split()[1])
                        break

            processes.append({
                "pid": pid,
                "name": comm,
                "cpu_ticks": total_ticks,
                "mem_rss_mb": round(rss_kb / 1024, 1),
            })
        except (FileNotFoundError, IndexError, ValueError, PermissionError):
            continue

    # Sort
    if sort_by == "mem":
        processes.sort(key=lambda p: p["mem_rss_mb"], reverse=True)
    else:
        processes.sort(key=lambda p: p["cpu_ticks"], reverse=True)

    return {
        "total_processes": len(processes),
        "sort_by": sort_by,
        "limit": limit,
        "processes": processes[:limit],
    }


@mcp.tool()
def kill_process(pid: int, sig: int = 15) -> dict:
    """
    Kill a process by PID. Requires root (Magisk su).
    Only SIGTERM (15) and SIGKILL (9) are allowed.
    System-critical processes (init, zygote, system_server) are protected.

    Args:
        pid: Process ID to kill.
        sig: Signal number — 15 (SIGTERM) or 9 (SIGKILL).
    """
    # Validate signal
    if sig not in (9, 15):
        return {"success": False, "error": f"Signal {sig} not allowed. Use 9 (SIGKILL) or 15 (SIGTERM)."}

    # Validate PID
    if pid in PROTECTED_PIDS:
        return {"success": False, "error": f"PID {pid} is protected (system-critical)."}

    # Check process name
    comm = _read_sys_file(Path(f"/proc/{pid}/comm"))
    if comm and comm.lower() in PROTECTED_NAMES:
        return {"success": False, "error": f"Process '{comm}' (PID {pid}) is system-critical and protected."}

    # Attempt kill
    try:
        os.kill(pid, sig)
        return {"success": True, "pid": pid, "signal": sig, "process_name": comm}
    except PermissionError:
        # Try with root
        try:
            result = subprocess.run(
                ["su", "-c", f"kill -{sig} {pid}"],
                capture_output=True, text=True, timeout=5,
            )
            return {
                "success": result.returncode == 0,
                "pid": pid,
                "signal": sig,
                "process_name": comm,
                "used_root": True,
            }
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            return {"success": False, "error": str(e)}
    except ProcessLookupError:
        return {"success": False, "error": f"PID {pid} does not exist."}


# ---------------------------------------------------------------------------
# Tools — Summary
# ---------------------------------------------------------------------------

@mcp.tool()
def device_summary() -> dict:
    """
    All-in-one system health snapshot.
    Combines battery, thermal, CPU, and memory info into a single response.
    Use for quick system health assessment before resource-heavy operations.
    """
    return {
        "battery": battery_status(),
        "thermal": thermal_status(),
        "memory": memory_usage(),
        "cpu_load": {
            "load_average": _read_sys_file(PROC_LOADAVG),
        },
        "timestamp": time.time(),
    }


# ---------------------------------------------------------------------------
# Resources
# ---------------------------------------------------------------------------

@mcp.resource("device://info")
def device_info() -> str:
    """Device hardware and OS information."""
    return json.dumps(
        {
            "platform": "Android Termux",
            "device": "Nothing Phone (2a)",
            "chipset": "MediaTek Dimensity 7200 Pro",
            "cpu_arch": "arm64-v8a (aarch64)",
            "gpu": "ARM Mali-G610 MC4",
            "ram_gb": 11.14,
            "storage_gb": 256,
            "monitored_paths": {
                "power_supply": str(POWER_SUPPLY_PATH),
                "thermal": str(THERMAL_PATH),
                "proc_stat": str(PROC_STAT),
                "proc_meminfo": str(PROC_MEMINFO),
            },
        },
        indent=2,
    )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run(transport="stdio")
