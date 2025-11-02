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

    arch = normalize_architecture(platform.architecture()[0])

    if system == "Windows":
        # Windows-specific details: edition, release, and build version
        edition = platform.win32_edition()
        release = platform.release()
        version = platform.version()
        return f"{system} {release} {edition} (Build {version}) {arch}".strip()

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
            return f"{system_name} {release} {arch}"

    elif system == "Darwin":
        # macOS: get human-readable version (e.g., 14.1 instead of Darwin 23.0.0)
        mac_version, *_ = platform.mac_ver()
        return f"macOS {mac_version or platform.release()} {arch}"

    # Other / unknown systems
    else:
        return f"{system} {arch}"

if __name__ == "__main__":
    print(get_system_info())
