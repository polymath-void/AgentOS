#!/usr/bin/env python3
import sys
import os
import subprocess
import shutil

args = sys.argv[1:]
is_build_script = False
out_file = None

for i, arg in enumerate(args):
    if arg.endswith("build.rs"):
        is_build_script = True
    if arg == "-o" and i + 1 < len(args):
        out_file = args[i+1]

pkg_name = os.environ.get("CARGO_PKG_NAME", "")

with open("/data/data/com.termux/files/home/Projects/local/agent/wrapper.log", "a") as log:
    log.write(f"PKG: {pkg_name}, out: {out_file}, args: {' '.join(args)}\n")

# If it's a build script for crossbeam-epoch, mock it
if is_build_script and out_file and "crossbeam-epoch" in pkg_name:
    with open(out_file, "w") as f:
        # Use explicit termux sh path
        f.write("#!/data/data/com.termux/files/usr/bin/sh\nexit 0\n")
    os.chmod(out_file, 0o755)
    with open("/data/data/com.termux/files/home/Projects/local/agent/wrapper.log", "a") as log:
        log.write(f"MOCKED crossbeam-epoch build.rs -> {out_file}\n")
    sys.exit(0)

# Otherwise, just run rustc
try:
    sys.exit(subprocess.call(args))
except Exception as e:
    print(f"Wrapper error: {e}", file=sys.stderr)
    sys.exit(1)
