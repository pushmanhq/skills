"""Negative fixtures verify actual packaging failures, not skill wording."""

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from scripts.validate import ROOT, resolve_inside, validate


class PackageValidationTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix="pushman-skill-test-")
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name) / "repo"
        shutil.copytree(ROOT, self.root, ignore=shutil.ignore_patterns(".git", ".venv", "__pycache__"))
        self.plugin = self.root / "plugins/pushman"
        self.skill = self.plugin / "skills/pushman"

    def mutate_json(self, relative, change):
        path = self.root / relative
        data = json.loads(path.read_text())
        change(data)
        path.write_text(json.dumps(data))

    def test_valid_package(self):
        validate(self.root)

    def test_plugin_version_mismatch(self):
        self.mutate_json("plugins/pushman/.claude-plugin/plugin.json", lambda d: d.update(version="9.0.0"))
        with self.assertRaisesRegex(ValueError, "Plugin version mismatch"):
            validate(self.root)

    def test_marketplace_version_mismatch(self):
        self.mutate_json(".claude-plugin/marketplace.json", lambda d: d["plugins"][0].update(version="9.0.0"))
        with self.assertRaisesRegex(ValueError, "Marketplace version mismatch"):
            validate(self.root)

    def test_broken_reference(self):
        (self.skill / "references/setup.md").unlink()
        with self.assertRaisesRegex(ValueError, "Broken link"):
            validate(self.root)

    def test_skill_reference_must_travel_with_skill(self):
        with (self.skill / "SKILL.md").open("a") as file:
            file.write("\n[Nonportable instructions](../../../../README.md)\n")
        with self.assertRaisesRegex(ValueError, "Link escapes portable scope"):
            validate(self.root)

    def test_no_implicit_mcp_dependency(self):
        self.mutate_json("plugins/pushman/.codex-plugin/plugin.json", lambda d: d.update(mcpServers="./.mcp.json"))
        with self.assertRaisesRegex(ValueError, "instruction-only"):
            validate(self.root)

    def test_undeclared_hook_is_rejected(self):
        path = self.plugin / "hooks/hooks.json"
        path.parent.mkdir()
        path.write_text('{"hooks": {}}')
        with self.assertRaisesRegex(ValueError, "Unexpected runtime file"):
            validate(self.root)

    def test_symlink_is_rejected(self):
        (self.skill / "references/extra.md").symlink_to(self.root / "README.md")
        with self.assertRaisesRegex(ValueError, "Symlink is not portable"):
            validate(self.root)

    def test_absolute_paths_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "Absolute path"):
            resolve_inside(self.plugin, str(self.root / "README.md"))

    def test_path_escape_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Path escapes package"):
            resolve_inside(self.plugin, "../../README.md")

    def test_personal_machine_paths_are_rejected(self):
        with (self.skill / "SKILL.md").open("a") as file:
            file.write("\nUse /Users/example/.config/private.json\n")
        with self.assertRaisesRegex(ValueError, "Private machine path"):
            validate(self.root)


if __name__ == "__main__":
    unittest.main()
