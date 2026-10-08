import contextlib
import os
import platform
import plistlib
import sys
import tempfile
import unittest
from unittest import mock

import system_info


def fake_winreg(values):
    winreg = mock.MagicMock()
    winreg.KEY_READ = 0x20019
    winreg.KEY_WOW64_64KEY = 0x0100

    def query_value(key, name):
        if name not in values:
            raise OSError(2, "value not found")
        return values[name], 1

    winreg.QueryValueEx.side_effect = query_value
    return winreg


def windows_registry(**overrides):
    info = {name: None for name in system_info.WINDOWS_REGISTRY_VALUES}
    info.update(
        ProductName="Windows 10 Pro",
        DisplayVersion="25H2",
        EditionID="Professional",
        CurrentBuildNumber="26200",
        CurrentMajorVersionNumber="10",
    )
    info.update(overrides)
    return info


class NormalizeArchitectureTests(unittest.TestCase):
    def test_known_machine_strings(self):
        cases = {
            "x86_64": "64-Bit",
            "amd64": "AMD64",
            "arm64": "ARM64",
            "aarch64": "ARM64",
        }
        for raw, expected in cases.items():
            with self.subTest(raw=raw):
                self.assertEqual(system_info.normalize_architecture(raw), expected)

    def test_matching_is_case_insensitive(self):
        self.assertEqual(system_info.normalize_architecture("X86_64"), "64-Bit")

    def test_unknown_machine_strings_pass_through(self):
        self.assertEqual(system_info.normalize_architecture("riscv64"), "riscv64")


class JoinPartsTests(unittest.TestCase):
    def test_drops_none_and_empty_parts(self):
        self.assertEqual(system_info.join_parts("a", None, "", "b"), "a b")

    def test_all_empty_returns_empty_string(self):
        self.assertEqual(system_info.join_parts(None, ""), "")

    def test_non_string_parts_are_coerced(self):
        self.assertEqual(system_info.join_parts("a", 5, None), "a 5")


class WindowsTests(unittest.TestCase):
    NO_REGISTRY = object()
    NO_EDITION_ATTRIBUTE = object()

    def patch_windows(self, registry=NO_REGISTRY, edition="Professional",
                      release="11", version="10.0.26200"):
        if edition is self.NO_EDITION_ATTRIBUTE:
            edition_patch = mock.patch.object(
                platform, "win32_edition", new=None, create=True
            )
        else:
            edition_patch = mock.patch.object(
                platform, "win32_edition", return_value=edition, create=True
            )
        stack = contextlib.ExitStack()
        for p in (
            mock.patch.object(platform, "system", return_value="Windows"),
            mock.patch.object(platform, "machine", return_value="AMD64"),
            mock.patch.object(platform, "release", return_value=release),
            mock.patch.object(platform, "version", return_value=version),
            edition_patch,
            mock.patch.object(
                system_info,
                "get_windows_registry_info",
                return_value=windows_registry() if registry is self.NO_REGISTRY
                else registry,
            ),
        ):
            stack.enter_context(p)
        return stack

    def test_reports_full_info(self):
        with self.patch_windows():
            self.assertEqual(
                system_info.get_system_info(),
                "Windows 11 25H2 Professional (Build 26200) AMD64",
            )

    def test_registry_edition_used_when_win32_edition_fails(self):
        with self.patch_windows(edition=None):
            self.assertEqual(
                system_info.get_system_info(),
                "Windows 11 25H2 Professional (Build 26200) AMD64",
            )

    def test_registry_edition_used_when_win32_edition_is_missing(self):
        with self.patch_windows(edition=self.NO_EDITION_ATTRIBUTE):
            self.assertEqual(
                system_info.get_system_info(),
                "Windows 11 25H2 Professional (Build 26200) AMD64",
            )

    def test_omits_undeterminable_edition(self):
        with self.patch_windows(
            windows_registry(EditionID=None),
            edition=None,
        ):
            self.assertEqual(
                system_info.get_system_info(),
                "Windows 11 25H2 (Build 26200) AMD64",
            )

    def test_omits_missing_feature_update(self):
        with self.patch_windows(windows_registry(DisplayVersion=None, ReleaseId=None)):
            self.assertEqual(
                system_info.get_system_info(),
                "Windows 11 Professional (Build 26200) AMD64",
            )

    def test_falls_back_to_release_id(self):
        with self.patch_windows(
            windows_registry(
                DisplayVersion=None,
                ReleaseId="2004",
                CurrentBuildNumber="19041",
            )
        ):
            self.assertEqual(
                system_info.get_system_info(),
                "Windows 10 2004 Professional (Build 19041) AMD64",
            )

    def test_server_editions_use_platform_release(self):
        with self.patch_windows(
            windows_registry(
                ProductName="Windows Server 2022 Standard",
                DisplayVersion=None,
                CurrentBuildNumber="20348",
            ),
            release="Server2022",
        ):
            self.assertEqual(
                system_info.get_system_info(),
                "Windows Server2022 Professional (Build 20348) AMD64",
            )

    def test_registry_unavailable_falls_back_to_platform(self):
        with self.patch_windows(registry=None):
            self.assertEqual(
                system_info.get_system_info(),
                "Windows 11 Professional (Build 26200) AMD64",
            )


class WindowsRegistryTests(unittest.TestCase):
    def test_reads_values_as_strings(self):
        values = {"DisplayVersion": "25H2", "CurrentMajorVersionNumber": 10}
        fake = fake_winreg(values)
        with mock.patch.object(platform, "system", return_value="Windows"), \
                mock.patch.dict(sys.modules, {"winreg": fake}):
            info = system_info.get_windows_registry_info()
        self.assertEqual(info["DisplayVersion"], "25H2")
        self.assertEqual(info["CurrentMajorVersionNumber"], "10")
        fake.OpenKey.assert_called_once_with(
            fake.HKEY_LOCAL_MACHINE,
            system_info.WINDOWS_REGISTRY_PATH,
            access=0x20019 | 0x0100,
        )

    def test_missing_values_are_none(self):
        with mock.patch.object(platform, "system", return_value="Windows"), \
                mock.patch.dict(sys.modules, {"winreg": fake_winreg({})}):
            info = system_info.get_windows_registry_info()
        self.assertIsNone(info["DisplayVersion"])
        self.assertIsNone(info["EditionID"])

    def test_unopenable_key_returns_none(self):
        broken = fake_winreg({})
        broken.OpenKey.side_effect = OSError
        with mock.patch.object(platform, "system", return_value="Windows"), \
                mock.patch.dict(sys.modules, {"winreg": broken}):
            self.assertIsNone(system_info.get_windows_registry_info())

    def test_returns_none_off_windows(self):
        with mock.patch.object(platform, "system", return_value="Linux"):
            self.assertIsNone(system_info.get_windows_registry_info())


class LinuxTests(unittest.TestCase):
    def patch_linux(self, os_release=None, os_release_error=None,
                    release="7.2.9-generic"):
        stack = contextlib.ExitStack()
        for p in (
            mock.patch.object(platform, "system", return_value="Linux"),
            mock.patch.object(platform, "machine", return_value="x86_64"),
            mock.patch.object(platform, "release", return_value=release),
        ):
            stack.enter_context(p)
        stack.enter_context(mock.patch.object(
            platform, "freedesktop_os_release",
            side_effect=os_release_error,
            return_value=os_release or {},
        ))
        return stack

    def test_pretty_name(self):
        with self.patch_linux(os_release={"PRETTY_NAME": "Ubuntu 26.04.1 LTS"}):
            self.assertEqual(system_info.get_system_info(), "Ubuntu 26.04.1 LTS 64-Bit")

    def test_name_and_version_fallback(self):
        with self.patch_linux(os_release={"NAME": "Arch Linux",
                                          "VERSION": "2026.10.01"}):
            self.assertEqual(system_info.get_system_info(), "Arch Linux 2026.10.01 64-Bit")

    def test_version_id_fallback_when_version_is_missing(self):
        with self.patch_linux(os_release={"NAME": "Debian GNU/Linux",
                                          "VERSION_ID": "13"}):
            self.assertEqual(system_info.get_system_info(), "Debian GNU/Linux 13 64-Bit")

    def test_name_only_fallback(self):
        with self.patch_linux(os_release={"NAME": "Alpine Linux"}):
            self.assertEqual(system_info.get_system_info(), "Alpine Linux 64-Bit")

    def test_missing_os_release_falls_back_to_kernel(self):
        with self.patch_linux(os_release_error=OSError):
            self.assertEqual(system_info.get_system_info(), "Linux 7.2.9-generic 64-Bit")

    def test_os_release_unavailable_on_old_python(self):
        with self.patch_linux(os_release_error=AttributeError):
            self.assertEqual(system_info.get_system_info(), "Linux 7.2.9-generic 64-Bit")

    def test_unparseable_os_release_falls_back_to_kernel(self):
        with self.patch_linux(os_release_error=ValueError):
            self.assertEqual(system_info.get_system_info(), "Linux 7.2.9-generic 64-Bit")

    def test_undeterminable_architecture_is_omitted(self):
        stack = self.patch_linux(os_release={"PRETTY_NAME": "Ubuntu 26.04.1 LTS"})
        with stack, mock.patch.object(platform, "machine", return_value=""):
            self.assertEqual(system_info.get_system_info(), "Ubuntu 26.04.1 LTS")


class MacOSTests(unittest.TestCase):
    def test_reports_mac_ver(self):
        with mock.patch.object(platform, "system", return_value="Darwin"), \
                mock.patch.object(platform, "machine", return_value="arm64"), \
                mock.patch.object(system_info, "get_macos_version",
                                  return_value="26.5.2"):
            self.assertEqual(system_info.get_system_info(), "macOS 26.5.2 ARM64")

    def test_labels_darwin_kernel_release_when_version_unknown(self):
        with mock.patch.object(platform, "system", return_value="Darwin"), \
                mock.patch.object(platform, "machine", return_value="arm64"), \
                mock.patch.object(system_info, "get_macos_version", return_value=None), \
                mock.patch.object(platform, "release", return_value="25.0.0"):
            self.assertEqual(system_info.get_system_info(), "macOS (Darwin 25.0.0) ARM64")


class MacOSVersionTests(unittest.TestCase):
    def test_prefers_mac_ver(self):
        with mock.patch.object(platform, "mac_ver", return_value=("26.5.2", "", "")):
            self.assertEqual(system_info.get_macos_version(), "26.5.2")

    def test_reads_version_from_plist(self):
        data = plistlib.dumps({"ProductUserVisibleVersion": "15.2"})
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "SystemVersion.plist")
            with open(path, "wb") as f:
                f.write(data)
            with mock.patch.object(platform, "mac_ver", return_value=("", "", "")), \
                    mock.patch.object(system_info, "MACOS_VERSION_PLIST", path):
                self.assertEqual(system_info.get_macos_version(), "15.2")

    def test_invalid_plist_returns_none(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "SystemVersion.plist")
            with open(path, "wb") as f:
                f.write(b"not a plist")
            with mock.patch.object(platform, "mac_ver", return_value=("", "", "")), \
                    mock.patch.object(system_info, "MACOS_VERSION_PLIST", path):
                self.assertIsNone(system_info.get_macos_version())

    def test_missing_plist_returns_none(self):
        with mock.patch.object(platform, "mac_ver", return_value=("", "", "")), \
                mock.patch.object(system_info, "MACOS_VERSION_PLIST",
                                  os.path.join("no", "such", "file.plist")):
            self.assertIsNone(system_info.get_macos_version())


class OtherSystemTests(unittest.TestCase):
    def test_generic_fallback_instead_of_none(self):
        with mock.patch.object(platform, "system", return_value="FreeBSD"), \
                mock.patch.object(platform, "machine", return_value="amd64"), \
                mock.patch.object(platform, "release", return_value="14.2"):
            self.assertEqual(system_info.get_system_info(), "FreeBSD 14.2 AMD64")


if __name__ == "__main__":
    unittest.main()
