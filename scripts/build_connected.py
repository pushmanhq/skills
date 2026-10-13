#!/usr/bin/env python3
"""Bundle the maintained skill with an existing registered ChatGPT app, offline."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re

from scripts.build_chatgpt import package_files as hosted_files, write_package
from scripts.validate import ROOT, SEMVER, require


APP_ID = re.compile(r"asdk_app_[0-9a-f]{32}")
PLUGIN_NAME = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")


def package_files(app_id: str, plugin_name: str, root: Path = ROOT,
                  version: str | None = None) -> dict[str, bytes]:
    # A plugin page's technical ID includes plugin_; the app mapping does not.
    app_id = app_id.removeprefix("plugin_")
    require(APP_ID.fullmatch(app_id) is not None, "Expected a registered asdk_app ID")
    require(0 < len(plugin_name) <= 64 and PLUGIN_NAME.fullmatch(plugin_name) is not None,
            "Expected the exact registered plugin name, without a marketplace suffix or path")
    source = hosted_files(root)
    portable = json.loads(source["plugin.json"])
    version = portable["version"] if version is None else version
    require(isinstance(version, str) and SEMVER.fullmatch(version) is not None, "Invalid connected version")
    extension = portable["extensions"]["com.openai"]
    # Keep the existing registration identity. This ZIP does not create a server,
    # an OAuth connection, or a second bundled MCP transport.
    manifest = {key: portable[key] for key in
                ("description", "author", "homepage", "repository", "license", "keywords")}
    manifest.update(name=plugin_name, version=version, skills="./skills/", apps="./.app.json",
                    interface=extension["interface"],
                    extensions={"com.openai": {"onboardingSkill": extension["onboardingSkill"]}})
    result = {name: data for name, data in source.items()
              if name.startswith(("assets/", "skills/"))}
    result[".codex-plugin/plugin.json"] = (json.dumps(manifest, indent=2) + "\n").encode()
    result[".app.json"] = (json.dumps({"apps": {plugin_name: {"id": app_id}}}, indent=2) + "\n").encode()
    return result


def build(output: Path, app_id: str, plugin_name: str, root: Path = ROOT,
          version: str | None = None) -> dict:
    files = package_files(app_id, plugin_name, root, version)
    manifest = json.loads(files[".codex-plugin/plugin.json"])
    return {**write_package(output, files), "version": manifest["version"],
            "source_version": json.loads(hosted_files(root)["plugin.json"])["version"],
            "plugin_name": manifest["name"]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--app-id", required=True, help="Existing asdk_app ID or plugin_asdk_app page ID")
    parser.add_argument("--plugin-name", required=True, help="Exact name from the existing registered plugin manifest")
    parser.add_argument("--version", required=True, help="Private wrapper version newer than the existing registration")
    args = parser.parse_args()
    print(json.dumps(build(args.output, args.app_id, args.plugin_name, version=args.version)))
