from __future__ import annotations

import platform

WINDOWS_REGISTRY_PATH = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion"
WINDOWS_REGISTRY_VALUES = (
    "ProductName",
    "DisplayVersion",
    "ReleaseId",
    "EditionID",
    "CurrentBuildNumber",
    "CurrentMajorVersionNumber",
)
WINDOWS_11_MIN_BUILD = 22000
MACOS_VERSION_PLIST = "/System/Library/CoreServices/SystemVersion.plist"


def normalize_architecture(arch: str) -> str:
    mapping = {
        "x86_64": "64-Bit",
        "amd64": "AMD64",
        "arm64": "ARM64",
        "aarch64": "ARM64",
    }
    return mapping.get(arch.lower(), arch)


def join_parts(*parts: str | None) -> str:
    return " ".join(str(part) for part in parts if part)


def get_windows_registry_info() -> dict[str, str | None] | None:
    if platform.system() != "Windows":
        return None
    try:
        import winreg

        with winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            WINDOWS_REGISTRY_PATH,
            access=winreg.KEY_READ | winreg.KEY_WOW64_64KEY,
        ) as key:
            info: dict[str, str | None] = {}
            for name in WINDOWS_REGISTRY_VALUES:
                try:
                    value, _ = winreg.QueryValueEx(key, name)
                    info[name] = str(value)
                except OSError:
                    info[name] = None
            return info
    except OSError:
        return None


def get_macos_version() -> str | None:
    version = platform.mac_ver()[0]
    if version:
        return version
    try:
        import plistlib
    except ImportError:
        return None
    try:
        with open(MACOS_VERSION_PLIST, "rb") as plist_file:
            info = plistlib.load(plist_file)
    except (OSError, plistlib.InvalidFileException, AttributeError):
        return None
    return info.get("ProductUserVisibleVersion")


def get_system_info() -> str:
    system = platform.system()
    arch = normalize_architecture(platform.machine())

    if system == "Windows":
        info = get_windows_registry_info() or {}
        build = info.get("CurrentBuildNumber") or platform.version().split(".")[-1]
        try:
            build_number = int(build)
        except ValueError:
            build_number = 0
        product = info.get("ProductName") or ""
        if "Server" in product:
            release = product.replace("Windows", "", 1).strip()
            edition = None
        else:
            if (
                info.get("CurrentMajorVersionNumber") == "10"
                and build_number >= WINDOWS_11_MIN_BUILD
            ):
                release = "11"
            else:
                release = info.get("CurrentMajorVersionNumber") or platform.release()
            win32_edition = getattr(platform, "win32_edition", None)
            edition = win32_edition() if win32_edition is not None else None
            edition = edition or info.get("EditionID")
        feature = info.get("DisplayVersion") or info.get("ReleaseId")
        return join_parts(
            system,
            release,
            feature,
            edition,
            f"(Build {build})",
            arch,
        )

    if system == "Linux":
        try:
            os_release = platform.freedesktop_os_release()
            if "PRETTY_NAME" in os_release:
                return join_parts(os_release["PRETTY_NAME"], arch)
            name = os_release.get("NAME", "Linux")
            version = os_release.get("VERSION") or os_release.get("VERSION_ID") or ""
            return join_parts(name, version, arch)
        except (AttributeError, OSError, ValueError):
            return join_parts(system, platform.release(), arch)

    if system == "Darwin":
        mac_version = get_macos_version()
        if mac_version:
            return join_parts("macOS", mac_version, arch)
        return join_parts("macOS", f"(Darwin {platform.release()})", arch)

    return join_parts(system, platform.release(), arch)


if __name__ == "__main__":
    print(get_system_info())
