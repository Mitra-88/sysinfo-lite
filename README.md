# SysLite 🖥️✨

**SysLite** is a tiny Python utility that tells you your OS and architecture.

## Why bother? 🤔

`platform.platform()` is okay. Mid. Works, but sometimes messy. SysLite gives you **exactly what you need**: OS, version, and architecture in one clean string. 💡

## Example Output 🎯

- Windows 11 Professional 64-Bit
- Fedora Linux 43 (Workstation Edition) 64-Bit
- macOS 15.7.1 ARM64

## Features ✨

* Works on **Windows**, **Linux**, and **macOS** 💻🍏🐧
* Normalizes architecture labels:
  * `x86_64` → `64-Bit`
  * `arm64` / `aarch64` → `ARM64`
* Handles Linux fallback nicely 🔄
* Zero dependencies. Pure Python 🐍

## How it works 🛠️

* Detects your OS with `platform.system()` 🖥️
* Maps raw architecture strings to readable ones 🔠
* Windows → adds edition & release 🪟
* Linux → tries distro info → fallback 🔄
* macOS → shows release + architecture 🍏

Basically, clean, simple, and doesn’t overcomplicate things. ✅
