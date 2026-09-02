---
name: termux-environment
description: Crucial instructions for operating within an Android Termux environment, covering path resolution, package management, and Termux-specific constraints.
---

# Termux Environment Skill

This skill provides specialized knowledge for operating within the Termux application on Android. 

## 1. Path Resolution
- **Prefix:** All absolute paths in Termux must be prefixed with `/data/data/com.termux/files`.
- **Home Directory:** The home directory is `/data/data/com.termux/files/home` (or `~`).
- **Usr Directory:** Binaries and libraries are located in `/data/data/com.termux/files/usr`.
- Avoid using standard Linux paths like `/bin`, `/usr/bin`, or `/var` unless you are explicitly in a chroot or proot environment.

## 2. Package Management
- Use `pkg` or `apt` for installing software. Prefer `pkg install <package_name>`.
- Keep in mind that some standard Linux packages might have different names or might not be available.

## 3. Storage and Android Integration
- **Shared Storage:** To access external Android storage (like the SD card or shared directories), use `termux-setup-storage`. This mounts storage to `~/storage`.
- Use the `termux-api` package and commands (e.g., `termux-clipboard-get`, `termux-battery-status`) to interact with Android hardware and system services.

## 4. Known Limitations
- The system libc is often bionic (Android's libc) or sometimes glibc depending on the specific Termux environment. If you encounter ELF header errors (e.g., `invalid ELF header` for `libc.so`), it usually means there is a mismatch between the binary and the installed libc, or a corrupted package.
- Avoid compiling native extensions that rely on standard Linux kernel headers without ensuring you have the specific Termux kernel headers installed.
