import hashlib
from pathlib import Path
import tempfile
import unittest
import zipfile
from scripts.build_chatgpt import build, package_files
from tests import test_validate as validation_fixtures


class HostedPackageTests(unittest.TestCase):
    def test_complete_deterministic_zip_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            first, second = Path(directory) / "first.zip", Path(directory) / "second.zip"
            receipt = build(first)
            build(second)
            self.assertEqual(first.read_bytes(), second.read_bytes())
            self.assertEqual(receipt["sha256"], hashlib.sha256(first.read_bytes()).hexdigest())
            with zipfile.ZipFile(first) as archive:
                self.assertEqual({name: archive.read(name) for name in archive.namelist()}, package_files())
                self.assertTrue(all(not name.startswith("/") and ".." not in Path(name).parts for name in archive.namelist()))
                self.assertNotIn("hooks/hooks.json", archive.namelist())
                self.assertNotIn(".app.json", archive.namelist())
                self.assertIn("skills/pushman/references/setup.md", archive.namelist())
            with self.assertRaises(FileExistsError):
                build(first)


class HostedNegativeTests(unittest.TestCase):
    setUp = validation_fixtures.PackageValidationTests.setUp
    mutate_json = validation_fixtures.PackageValidationTests.mutate_json

    def test_hosted_version_mismatch(self):
        self.mutate_json("distributions/chatgpt/plugin.json", lambda d: d.update(version="9.0.0"))
        with self.assertRaisesRegex(ValueError, "Hosted plugin version mismatch"):
            package_files(self.root)

    def test_embedded_token_header_is_rejected(self):
        self.mutate_json("distributions/chatgpt/mcp.json", lambda d: d["mcpServers"]["pushman"].update(headers={"Authorization": "Bearer synthetic"}))
        with self.assertRaisesRegex(ValueError, "authorization headers"):
            package_files(self.root)

    def test_unprotected_hosted_endpoint_is_rejected(self):
        self.mutate_json("distributions/chatgpt/mcp.json", lambda d: d["mcpServers"]["pushman"]["extensions"]["com.openai"]["auth"].update(type="none"))
        with self.assertRaisesRegex(ValueError, "requires OAuth"):
            package_files(self.root)

    def test_localhost_endpoint_is_rejected(self):
        self.mutate_json("distributions/chatgpt/mcp.json", lambda d: d["mcpServers"]["pushman"].update(url="http://localhost/mcp"))
        with self.assertRaisesRegex(ValueError, "transport or endpoint"):
            package_files(self.root)
