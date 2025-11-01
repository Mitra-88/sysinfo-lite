import platform

def get_system_info():
    system = platform.system()
    arch = normalize_architecture(platform.architecture()[0])

    if system == "Windows":
        edition = platform.win32_edition()
        return f"{system} {edition} {arch}"

    elif system == "Linux":
        os_release = platform.freedesktop_os_release()
        name = os_release.get("PRETTY_NAME")
        if not name:
            name = f"{os_release.get('NAME', 'Linux')} {os_release.get('VERSION', '')}".strip()
        return f"{name} {arch}"

    elif system == "Darwin":
        return f"macOS {platform.release()} {normalize_architecture(platform.machine())}"

    else:
        return f"{system} {arch}"

def normalize_architecture(arch):
    mapping = {
        "x86_64": "64-Bit",
        "AMD64": "64-Bit",
        "arm64": "ARM64",
        "aarch64": "ARM64",
        "64bit": "64-Bit",
    }
    return mapping.get(arch, arch)

system_info = get_system_info()
