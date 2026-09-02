# Analysis Report: `android-tools` YAML Frontmatter Header Audit

**Milestone**: M1 (R1 Spec Audit & Frontmatter Fixes)  
**Target Category**: `/data/data/com.termux/files/home/skills-workspace/user-skills/android-tools/`  
**Explorer Agent**: Explorer 1 (`explorer_m1_1`)  
**Date**: 2026-08-06  

---

## 1. Overview & Summary of Findings

A comprehensive audit was performed across all 16 sub-skills located under `user-skills/android-tools/`.

- **Total Sub-skills Audited**: 16
- **Sub-skills with Existing Valid YAML Frontmatter**: 4
- **Sub-skills Missing YAML Frontmatter Headers**: 12

The 4 existing sub-skills (`android-flashing-tools`, `android-kernel-build`, `android-scp-transfer`, `phone-ssh-connect`) already possess valid `---` delimited YAML headers containing `name` and `description` attributes.

The remaining 12 sub-skills currently lack YAML frontmatter headers and begin directly with Markdown `# Skill: ...` top-level headings. Adding standardized YAML frontmatter headers to these 12 sub-skills will bring the entire `android-tools` category into 100% compliance with AI agent auto-discovery schemas.

---

## 2. Audit Matrix of All 16 Sub-Skills

| # | Sub-Skill Directory | Header Status | Existing / Recommended `name` | Summary / Recommended `description` |
|---|-------------------|---------------|-----------------------------|-------------------------------------|
| 1 | `android-flashing-tools` | ✅ Present | `android-flashing-tools` | Instructions and reference workflows for Android bootloader unlocking, firmware flashing (fastboot/boot.img/vbmeta), ADB shell scripting, and device diagnostics. |
| 2 | `android-kernel-build` | ✅ Present | `android-kernel-build` | Cross-compilation protocol for custom Android GKI Linux Kernels (arm64/AArch64) using Clang-18 and LLVM on Linux hosts. |
| 3 | `android-scp-transfer` | ✅ Present | `android-scp-transfer` | Transfer files between Android devices (Termux/SSH) and PC using SCP over local Wi-Fi or ADB. |
| 4 | `debug-selinux-denials` | ❌ Missing | `debug-selinux-denials` | Capture, analyze, and craft precise SEPolicy rules (.te files) for AVC denials without compromising Android security. |
| 5 | `decompile-apk` | ❌ Missing | `decompile-apk` | Decompile Android APK files using Apktool and JADX to reconstruct AndroidManifest.xml, resources, Smali assembly, and Java code. |
| 6 | `diagnose-brick-state` | ❌ Missing | `diagnose-brick-state` | Differentiate between soft brick (bootloop, fastboot accessible) and hard brick (EDL QDLoader 9008, MTK Preloader) states for Android devices. |
| 7 | `execute-aosp-build` | ❌ Missing | `execute-aosp-build` | Compile full Android Open Source Project (AOSP) system images for hardware targets or Cuttlefish emulator. |
| 8 | `flash-factory-images` | ❌ Missing | `flash-factory-images` | Restore an Android device to stock factory software by flashing official partition binaries. |
| 9 | `frida-tracing` | ❌ Missing | `frida-tracing` | Dynamically instrument Android framework services and system_server using Frida hooks. |
| 10 | `implement-aidl-hal` | ❌ Missing | `implement-aidl-hal` | Create AIDL-defined Hardware Abstraction Layer (HAL) service for Android Treble architecture. |
| 11 | `kernel-ftrace-debugging` | ❌ Missing | `kernel-ftrace-debugging` | Diagnose Android kernel crashes, driver latency spikes, and I/O bottlenecks using ftrace, pstore, and kasan. |
| 12 | `map-android-architecture` | ❌ Missing | `map-android-architecture` | Analyze and describe the function of any major Android OS component (Zygote, Binder, HAL, ART) detailing role and IPC interactions. |
| 13 | `phone-ssh-connect` | ✅ Present | `phone-ssh-connect` | Setup and connect a mobile phone (Android/iOS) to the host machine over local Wi-Fi SSH. |
| 14 | `recover-via-edl` | ❌ Missing | `recover-via-edl` | Unbrick hard-bricked Qualcomm device in Emergency Download mode using Firehose programmer and QFIL. |
| 15 | `treble-vts-cts` | ❌ Missing | `treble-vts-cts` | Run Vendor Test Suite (VTS) and Compatibility Test Suite (CTS) to ensure GSI compatibility and Android compliance. |
| 16 | `unlock-bootloader` | ❌ Missing | `unlock-bootloader` | Enable OEM unlock and issue fastboot protocols to unlock bootloader for custom system flashing. |

---

## 3. Exact Recommended YAML Frontmatter Snippets for the 12 Missing Sub-Skills

Below are the exact YAML blocks to prepend at Line 1 of each missing `SKILL.md` file.

### 1. `user-skills/android-tools/debug-selinux-denials/SKILL.md`
```yaml
---
name: debug-selinux-denials
description: Capture, analyze, and craft precise SEPolicy rules (.te files) for AVC denials without compromising Android security.
---
```

### 2. `user-skills/android-tools/decompile-apk/SKILL.md`
```yaml
---
name: decompile-apk
description: Decompile Android APK files using Apktool and JADX to reconstruct AndroidManifest.xml, resources, Smali assembly, and Java code.
---
```

### 3. `user-skills/android-tools/diagnose-brick-state/SKILL.md`
```yaml
---
name: diagnose-brick-state
description: Differentiate between soft brick (bootloop, fastboot accessible) and hard brick (EDL QDLoader 9008, MTK Preloader) states for Android devices.
---
```

### 4. `user-skills/android-tools/execute-aosp-build/SKILL.md`
```yaml
---
name: execute-aosp-build
description: Compile full Android Open Source Project (AOSP) system images for hardware targets or Cuttlefish emulator.
---
```

### 5. `user-skills/android-tools/flash-factory-images/SKILL.md`
```yaml
---
name: flash-factory-images
description: Restore an Android device to stock factory software by flashing official partition binaries.
---
```

### 6. `user-skills/android-tools/frida-tracing/SKILL.md`
```yaml
---
name: frida-tracing
description: Dynamically instrument Android framework services and system_server using Frida hooks.
---
```

### 7. `user-skills/android-tools/implement-aidl-hal/SKILL.md`
```yaml
---
name: implement-aidl-hal
description: Create AIDL-defined Hardware Abstraction Layer (HAL) service for Android Treble architecture.
---
```

### 8. `user-skills/android-tools/kernel-ftrace-debugging/SKILL.md`
```yaml
---
name: kernel-ftrace-debugging
description: Diagnose Android kernel crashes, driver latency spikes, and I/O bottlenecks using ftrace, pstore, and kasan.
---
```

### 9. `user-skills/android-skills/map-android-architecture/SKILL.md`
```yaml
---
name: map-android-architecture
description: Analyze and describe the function of any major Android OS component (Zygote, Binder, HAL, ART) detailing role and IPC interactions.
---
```

### 10. `user-skills/android-tools/recover-via-edl/SKILL.md`
```yaml
---
name: recover-via-edl
description: Unbrick hard-bricked Qualcomm device in Emergency Download mode using Firehose programmer and QFIL.
---
```

### 11. `user-skills/android-tools/treble-vts-cts/SKILL.md`
```yaml
---
name: treble-vts-cts
description: Run Vendor Test Suite (VTS) and Compatibility Test Suite (CTS) to ensure GSI compatibility and Android compliance.
---
```

### 12. `user-skills/android-tools/unlock-bootloader/SKILL.md`
```yaml
---
name: unlock-bootloader
description: Enable OEM unlock and issue fastboot protocols to unlock bootloader for custom system flashing.
---
```

---

## 4. Implementation Guidance for Implementer Agent

- When prepending the YAML frontmatter headers to the 12 files, ensure a newline separates the closing `---` and the existing content `# Skill: ...`.
- No modification of existing content below Line 1 is necessary.
- Read-only constraint: Explorer 1 has not modified any file in `user-skills/android-tools/`.
