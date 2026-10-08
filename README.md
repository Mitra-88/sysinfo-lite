# SysLite 🖥️✨

**SysLite** is a tiny Python utility that tells you your OS and architecture.

Works on **Python 3.7+**. Windows 11 is detected from the registry, so it reports correctly on any Python version: no 3.12+ requirement.

## Why bother? 🤔

`platform.platform()` works, but it’s messy and mid-tier. SysLite, on the other hand, gives you **precisely what you need** OS, version, and architecture all in one clean, readable string.

## Example Output 🎯

- Windows 11 25H2 Professional (Build 26200) AMD64
- Ubuntu 26.04.1 LTS 64-Bit
- macOS 26.7.1 ARM64

## Features ✨

* Focused on **64-bit systems** 🎯
* Works on **Windows**, **Linux**, and **macOS**, with a generic fallback everywhere else 💻🍏🐧
* Always returns a plain string: never `None`, never crashes on odd platforms ✅
* Detects Windows 11 on any Python version via the registry 🪟
* Windows edition from `platform.win32_edition()`, with the registry as fallback 🪟
* Normalizes architecture labels:
  * `x86_64` → `64-Bit`
  * `arm64` / `aarch64` → `ARM64`
* Layered fallbacks: `os-release` → kernel on Linux, `mac_ver` → `SystemVersion.plist` on macOS 🔄
* No external dependencies (standard library only) 🐍

## How it works 🛠️

* Detects your OS with `platform.system()` 🖥️
* Windows → version, edition & feature update read from the registry 🪟
* Linux → `os-release` pretty name → name/version → kernel release 🔄
* macOS → `platform.mac_ver()` → `SystemVersion.plist` → labeled Darwin release 🍏

## Tests 🧪

The platform calls are mocked, so the suite runs on any OS:

```
python -m unittest discover -v
```

CI runs the suite on Ubuntu 24.04 and 26.04 (x64 and Arm64), Windows Server 2022 and 2025, and macOS 26 (Arm64 and Intel), with Python 3.10, 3.12, and 3.14.

Basically, clean, simple, and doesn’t overcomplicate things. ✅
