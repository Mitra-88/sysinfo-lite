import platform

def get_system_info():
    system = platform.system()
    raw_arch = platform.architecture()[0]
    arch = normalize_architecture(raw_arch)

    if system == "Windows":
        edition = platform.win32_edition()
        return f"{system} {edition} {arch}".strip()

    elif system == "Linux":
        try:
            os_release = platform.freedesktop_os_release()

            # PART 1 — PRETTY_NAME
            if "PRETTY_NAME" in os_release:
                return f"{os_release['PRETTY_NAME']} {arch}"

            # PART 2 — NAME + VERSION fallback
            name = os_release.get("NAME", "Linux")
            version = os_release.get("VERSION", "")
            if name or version:
                return f"{name} {version} {arch}".strip()

        except OSError:
            # PART 3 — full fallback if freedesktop_os_release fails
            system_name = platform.system()
            release = platform.release()
            raw_arch = platform.architecture()[0]
            return f"{system_name} {release} {normalize_architecture(raw_arch)}"

    elif system == "Darwin":
        return f"macOS {platform.release()} {arch}"

    # Other / unknown systems
    else:
        return f"{system} {arch}"

def normalize_architecture(arch):
    mapping = {
        "x86_64": "64-Bit",
        "amd64": "64-Bit",
        "arm64": "ARM64",
        "aarch64": "ARM64",
        "64bit": "64-Bit",
    }
    return mapping.get(arch.lower(), arch)

system_info = get_system_info()
