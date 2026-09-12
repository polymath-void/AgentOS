import sys
import os
import argparse
import json
import asyncio

from compute_res.core.manifest import ModuleManifest
from compute_res.core.sandbox import WASMSandboxRunner
from compute_res.sdk.client import ComputeResClient

def build_skill_package(source_path: str, name: str, version: str = "1.0.0", fuel: int = 10000000) -> str:
    """Packages a skill directory or source file into a compute-res.json bundle."""
    if not os.path.exists(source_path):
        print(f"❌ Error: Source path '{source_path}' does not exist.")
        sys.exit(1)

    out_dir = os.path.join(os.path.dirname(os.path.abspath(source_path)), f"{name}_bundle")
    os.makedirs(out_dir, exist_ok=True)

    manifest = ModuleManifest(
        name=name,
        version=version,
        fuel_limit=fuel,
        memory_limit_mb=64,
        permissions=["filesystem:read", "network:outbound"],
        entrypoint="run",
        description=f"Auto-packaged skill module '{name}'"
    )

    manifest_path = os.path.join(out_dir, "compute-res.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest.to_dict(), f, indent=2)

    print(f"✅ Successfully packaged skill '{name}' v{version} into {out_dir}")
    print(f"   Manifest created at: {manifest_path}")
    return out_dir

def main():
    parser = argparse.ArgumentParser(description="ComputeRes AI Operating System CLI Tool")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Command: boot
    boot_parser = subparsers.add_parser("boot", help="Boot the ComputeRes Kernel daemon")

    # Command: build
    build_parser = subparsers.add_parser("build", help="Package a skill or binary into a compute-res.json bundle")
    build_parser.add_argument("--source", required=True, help="Path to source python file or skill directory")
    build_parser.add_argument("--name", required=True, help="Name of the skill module")
    build_parser.add_argument("--version", default="1.0.0", help="Version string")
    build_parser.add_argument("--fuel", type=int, default=10000000, help="Fuel allocation limit")

    # Command: status
    status_parser = subparsers.add_parser("status", help="Check ComputeRes kernel status")

    args = parser.parse_args()

    if args.command == "build":
        build_skill_package(args.source, args.name, args.version, args.fuel)

    elif args.command == "boot":
        print("🚀 Booting ComputeRes Kernel Daemon...")
        from compute_res.orchestration.kernel import main as boot_kernel
        boot_kernel()

    elif args.command == "status":
        async def _check():
            client = ComputeResClient()
            res = await client.execute_dynamic_code("def run(**kwargs): return {'kernel': 'ONLINE'}")
            print("ComputeRes Kernel Status:", res)
        asyncio.run(_check())

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
