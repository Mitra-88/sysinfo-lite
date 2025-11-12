import platform

def normalize_architecture(arch):
    mapping = {
        "x86_64": "64-Bit",
        "amd64": "64-Bit",
        "arm64": "ARM64",
        "aarch64": "ARM64",
        "64bit": "64-Bit",
    }
    return mapping.get(arch.lower(), arch)

def get_system_info():
    system = platform.system()

    arch = normalize_architecture(platform.machine())

    if system == "Windows":
        # Windows 11 Professional (Build 10.0.26200) 64-Bit
        edition = platform.win32_edition()
        release = platform.release()
        version = platform.version()
        return f"{system} {release} {edition} (Build {version}) {arch}".strip()

    elif system == "Linux":
        try:
            os_release = platform.freedesktop_os_release()

            # PART 1 — PRETTY_NAME
            # Pop!_OS 22.04 LTS 64-Bit
            if "PRETTY_NAME" in os_release:
                return f"{os_release['PRETTY_NAME']} {arch}"

            # PART 2 — NAME + VERSION fallback
            # Arch Linux 64-Bit
            name = os_release.get("NAME", "Linux")
            version = os_release.get("VERSION", "")
            if name or version:
                return f"{name} {version} {arch}".strip()

        except OSError:
            # PART 3 — full fallback if freedesktop_os_release fails
            # Linux 6.17.7-generic 64-Bit 
            system_name = platform.system()
            release = platform.release()
            return f"{system_name} {release} {arch}"

    elif system == "Darwin":
        # macOS 26.1 64-Bit
        mac_version, *_ = platform.mac_ver()
        return f"macOS {mac_version or platform.release()} {arch}"

    # Other / unknown systems
    # FreeBSD 14.0 64-Bit
    else:
        return f"{system} {arch}"

if __name__ == "__main__":
    print(get_system_info())
