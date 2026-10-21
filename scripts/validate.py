#!/usr/bin/env python3
"""Validate the portable, instruction-only Pushman package without network calls."""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit

import yaml


ROOT = Path(__file__).resolve().parents[1]
IGNORED = {".git", ".venv", "__pycache__"}
SEMVER = re.compile(r"(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def read_json(path: Path) -> dict:
    result = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(result, dict), f"Expected object: {path.name}")
    return result


def resolve_inside(base: Path, relative: str) -> Path:
    require(isinstance(relative, str) and bool(relative), "Missing relative path")
    require(not Path(relative).is_absolute(), f"Absolute path: {relative}")
    target = (base / relative).resolve()
    require(target.is_relative_to(base.resolve()), f"Path escapes package: {relative}")
    require(target.exists(), f"Missing path: {relative}")
    return target


def tracked_candidates(root: Path):
    for directory, dirs, files in os.walk(root):
        dirs[:] = [name for name in dirs if name not in IGNORED]
        for name in dirs + files:
            path = Path(directory) / name
            require(not path.is_symlink(), f"Symlink is not portable: {path.relative_to(root)}")
        for name in files:
            yield Path(directory) / name


def validate(root: Path = ROOT) -> None:
    root = root.resolve()
    plugin = root / "plugins/pushman"
    codex = read_json(plugin / ".codex-plugin/plugin.json")
    claude = read_json(plugin / ".claude-plugin/plugin.json")
    cm = read_json(root / ".agents/plugins/marketplace.json")
    am = read_json(root / ".claude-plugin/marketplace.json")

    require(codex.get("name") == claude.get("name") == plugin.name, "Plugin name mismatch")
    version = codex.get("version", "")
    require(isinstance(version, str) and SEMVER.fullmatch(version) is not None, "Invalid release version")
    require(claude.get("version") == version, "Plugin version mismatch")
    for field in ("description", "author", "homepage", "repository", "license", "skills"):
        require(bool(codex.get(field)) and codex.get(field) == claude.get(field), f"Manifest mismatch: {field}")
    require(codex["repository"] == "https://github.com/pushmanhq/skills", "Wrong repository")
    require(codex["license"] == "MIT", "Wrong license")
    require(codex["skills"] == "./skills/", "Wrong skill discovery path")
    require(resolve_inside(plugin, codex["skills"]).is_dir(), "Skills must be a directory")
    for manifest in (codex, claude):
        require(not ({"mcpServers", "apps", "hooks", "commands", "agents"} & manifest.keys()),
                "Package must remain instruction-only")

    require(cm.get("name") == am.get("name") == "pushman-skills", "Marketplace name mismatch")
    require(len(cm.get("plugins", [])) == len(am.get("plugins", [])) == 1, "Expected one plugin")
    ce, ae = cm["plugins"][0], am["plugins"][0]
    require(ce.get("name") == ae.get("name") == "pushman", "Marketplace plugin mismatch")
    require(ce.get("source") == {"source": "local", "path": "./plugins/pushman"}, "Wrong Codex source")
    require(ae.get("source") == "./plugins/pushman", "Wrong Claude source")
    require(resolve_inside(root, ae["source"]) == plugin, "Wrong plugin path")
    require(ae.get("version") == version, "Marketplace version mismatch")
    require(ce.get("policy") == {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
            "Unexpected installation policy")
    require(ce.get("category") == "Productivity", "Missing category")

    hosted = root / "distributions/chatgpt"
    portable = read_json(hosted / "plugin.json")
    require(portable.get("name") == "pushman" and portable.get("version") == version,
            "Hosted plugin version mismatch")
    require(portable.get("$schema") == "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json",
            "Missing portable plugin schema")
    extension = portable.get("extensions", {}).get("com.openai", {})
    require(not ({"apps", "hooks"} & extension.keys()), "Hosted plugin cannot contain app mappings or hooks")
    require(extension.get("onboardingSkill") == "./skills/pushman/SKILL.md", "Wrong hosted onboarding skill")
    require(extension.get("interface", {}).get("privacyPolicyURL") == "https://app.pushman.io/privacy/",
            "Wrong hosted privacy URL")
    require(resolve_inside(hosted, "./assets/icon.png").is_file(), "Missing hosted icon")
    connection = read_json(hosted / "mcp.json")
    require(connection.get("$schema") == "https://agent-plugins.org/schemas/1.0.0/mcp.schema.json",
            "Missing portable MCP schema")
    servers = connection.get("mcpServers", {})
    require(list(servers) == ["pushman"], "Expected exactly one hosted server")
    server = servers["pushman"]
    require(server.get("type") == "streamable-http" and server.get("url") == "https://app.pushman.io/mcp",
            "Wrong hosted MCP transport or endpoint")
    require(not server.get("headers"), "Hosted package cannot embed authorization headers")
    auth = server.get("extensions", {}).get("com.openai", {}).get("auth", {})
    require(auth.get("type") == "oauth" and auth.get("client") == {"mode": "cimd"},
            "Hosted MCP requires OAuth CIMD without client credentials")
    require(auth.get("resource") == server["url"], "Wrong hosted OAuth resource")
    require(auth.get("baseScopes") == ["push", "devices:read", "history:read", "usage:read", "sender:read", "sender:manage"],
            "Wrong hosted OAuth scope contract")
    require(not ({"clientSecret", "token", "apiKey"} & auth.keys()), "Hosted package cannot contain credentials")

    skill = plugin / "skills/pushman"
    require(list((plugin / "skills").glob("*/SKILL.md")) == [skill / "SKILL.md"], "Expected one Pushman skill")
    text = (skill / "SKILL.md").read_text(encoding="utf-8")
    parts = text.split("---", 2)
    require(len(parts) == 3 and not parts[0].strip(), "Missing skill frontmatter")
    metadata = yaml.safe_load(parts[1])
    require(isinstance(metadata, dict), "Invalid skill metadata")
    require(metadata.get("name") == skill.name, "Skill name mismatch")
    require(isinstance(metadata.get("description"), str) and 0 < len(metadata["description"]) <= 1024,
            "Invalid skill description")
    require(metadata.get("license") == "MIT", "Skill license mismatch")
    require(bool(parts[2].strip()), "Empty skill body")
    ui = yaml.safe_load((skill / "agents/openai.yaml").read_text(encoding="utf-8"))
    interface = ui["interface"]
    require(interface.get("display_name") == "Pushman", "Missing skill display name")
    require(25 <= len(interface.get("short_description", "")) <= 64, "Invalid short description")
    require("$pushman" in interface.get("default_prompt", ""), "Prompt must name the skill")
    require(ui.get("policy", {}).get("allow_implicit_invocation", True) is True,
            "Do not disable ordinary skill discovery")
    require("dependencies" not in ui, "MCP must remain optional")

    files = list(tracked_candidates(root))
    for path in files:
        if path.is_relative_to(plugin):
            relative = path.relative_to(plugin)
            is_manifest = str(relative) in {".codex-plugin/plugin.json", ".claude-plugin/plugin.json"}
            is_instruction = path.is_relative_to(skill) and (path.suffix == ".md" or path == skill / "agents/openai.yaml")
            require(is_manifest or is_instruction, f"Unexpected runtime file: {relative}")
        if path.suffix != ".md":
            continue
        content = path.read_text(encoding="utf-8")
        require("[TODO:" not in content, f"Unfinished scaffold: {path.name}")
        require("/Users/" not in content and "C:\\Users\\" not in content, f"Private machine path: {path.name}")
        for link in re.findall(r"!?\[[^\]]*\]\(([^)]+)\)", content):
            url = urlsplit(link)
            if url.scheme or url.netloc or not url.path:
                continue
            target = (path.parent / unquote(url.path)).resolve()
            boundary = skill if path.is_relative_to(skill) else root
            require(target.is_relative_to(boundary), f"Link escapes portable scope: {link}")
            require(target.exists(), f"Broken link in {path.name}: {link}")


if __name__ == "__main__":
    try:
        validate()
    except (ValueError, KeyError, TypeError, OSError, yaml.YAMLError) as error:
        raise SystemExit(f"Validation failed: {error}") from error
    print("Pushman manifests, aligned versions, hosted OAuth configuration, skill links and local instruction-only boundary passed.")
