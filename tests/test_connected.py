import json
from pathlib import Path
import tempfile
import unittest
import zipfile

from scripts.build_chatgpt import package_files as hosted_files
from scripts.build_connected import build, package_files


class ConnectedPackageTests(unittest.TestCase):
    app_id = "asdk_app_" + "0" * 32  # Synthetic registration; never contacts ChatGPT.
    plugin_name = "dev-" + "0" * 32

    def test_preserves_registration_and_complete_skill_without_bundled_server(self):
        files = package_files(self.app_id, self.plugin_name)
        manifest = json.loads(files[".codex-plugin/plugin.json"])
        self.assertEqual(manifest["name"], self.plugin_name)
        self.assertEqual(manifest["apps"], "./.app.json")
        self.assertEqual(json.loads(files[".app.json"]),
                         {"apps": {self.plugin_name: {"id": self.app_id}}})
        source = hosted_files()
        self.assertEqual({name: data for name, data in files.items()
                          if name.startswith(("skills/", "assets/"))},
                         {name: data for name, data in source.items()
                          if name.startswith(("skills/", "assets/"))})
        self.assertNotIn("mcp.json", files)
        self.assertNotIn(".mcp.json", files)
        self.assertNotIn("hooks", manifest)

    def test_complete_deterministic_zip_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            first, second = Path(directory) / "first.zip", Path(directory) / "second.zip"
            receipt = build(first, self.app_id, self.plugin_name)
            build(second, self.app_id, self.plugin_name)
            self.assertEqual(first.read_bytes(), second.read_bytes())
            self.assertEqual(receipt["files"], 6)
            with zipfile.ZipFile(first) as archive:
                self.assertEqual({name: archive.read(name) for name in archive.namelist()},
                                 package_files(self.app_id, self.plugin_name))
            with self.assertRaises(FileExistsError):
                build(first, self.app_id, self.plugin_name)

    def test_accepts_the_exact_registered_plugin_page_id(self):
        self.assertEqual(package_files("plugin_" + self.app_id, self.plugin_name),
                         package_files(self.app_id, self.plugin_name))

    def test_rejects_wrong_app_references_and_plugin_paths(self):
        for app in ["Plugin_" + "0" * 32, "https://example.com/mcp", self.app_id + "/", "asdk_app_../other"]:
            with self.subTest(app=app), self.assertRaisesRegex(ValueError, "registered asdk_app"):
                package_files(app, self.plugin_name)
        for name in ["../pushman", "pushman@personal", "", "x" * 65]:
            with self.subTest(name=name), self.assertRaisesRegex(ValueError, "exact registered plugin name"):
                package_files(self.app_id, name)

    def test_private_wrapper_version_can_follow_existing_registration(self):
        files = package_files(self.app_id, self.plugin_name, version="1.0.1")
        self.assertEqual(json.loads(files[".codex-plugin/plugin.json"])["version"], "1.0.1")
        with self.assertRaisesRegex(ValueError, "Invalid connected version"):
            package_files(self.app_id, self.plugin_name, version="../1")
