# SysLite

A lightweight Python utility that returns a clean, human-readable string of the current operating system and architecture.

## Example Output
- `Windows Pro 64-Bit`
- `Ubuntu 24.04.3 LTS 64-Bit`
- `macOS 23.5.0 ARM64`

## Usage
```python
from system_info import system_info
print(system_info)
```

## Why?
Because `platform.platform()` is messy. This gives you just what you need—no noise.
