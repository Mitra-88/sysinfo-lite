# SysLite 🖥️✨

**SysLite** is a tiny Python utility that tells you your OS and architecture.

> ⚠️ **Note:** Windows 11 detection requires **Python 3.12+**. Older Python versions report it as Windows 10.

## Why bother? 🤔

`platform.platform()` works, but it’s messy and mid-tier. SysLite, on the other hand, gives you **precisely what you need** OS, version, and architecture all in one clean, readable string.

## Example Output 🎯

- Windows 11 25H2 Professional (Build 10.0.26200) AMD64
- Ubuntu 24.04.4 LTS 64-Bit
- macOS 26.4.1 ARM64

## Features ✨

* Works on **Windows**, **Linux**, and **macOS** 💻🍏🐧
* Normalizes architecture labels:
  * `x86_64` → `64-Bit`
  * `arm64` / `aarch64` → `ARM64`
* Handles Linux fallback nicely 🔄
* No external dependencies (standard library only) 🐍

## How it works 🛠️

* Detects your OS with `platform.system()` 🖥️
* Maps raw architecture strings to readable ones 🔠
* Windows → adds edition & release 🪟
* Linux → tries distro info → fallback 🔄
* macOS → shows release + architecture 🍏

Basically, clean, simple, and doesn’t overcomplicate things. ✅
