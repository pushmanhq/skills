#!/usr/bin/env python3
"""Build the complete hosted Pushman plugin ZIP; never install or connect it."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import zipfile
from scripts.validate import ROOT, validate


def package_files(root: Path = ROOT) -> dict[str, bytes]:
    root = root.resolve()
    validate(root)
    distribution = root / "distributions/chatgpt"
    skill = root / "plugins/pushman/skills/pushman"
    result = {"plugin.json": (distribution / "plugin.json").read_bytes(),
              "mcp.json": (distribution / "mcp.json").read_bytes(),
              "assets/icon.png": (distribution / "assets/icon.png").read_bytes()}
    for path in sorted(skill.rglob("*")):
        if path.is_symlink():
            raise ValueError("Hosted package cannot contain symlinks")
        if path.is_file():
            result["skills/pushman/" + path.relative_to(skill).as_posix()] = path.read_bytes()
    return result


def build(output: Path, root: Path = ROOT) -> dict:
    files = package_files(root)
    output.parent.mkdir(parents=True, exist_ok=True)
    # Refuse overwrite so an earlier uploaded release remains identifiable.
    with output.open("xb") as stream, zipfile.ZipFile(stream, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, data in sorted(files.items()):
            info = zipfile.ZipInfo(name, (1980, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, data, compresslevel=9)
    with zipfile.ZipFile(output) as archive:
        if archive.testzip() is not None or {name: archive.read(name) for name in archive.namelist()} != files:
            raise ValueError("Hosted ZIP read-back differs")
    return {"path": str(output.resolve()), "sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
            "files": len(files), "version": json.loads(files["plugin.json"])["version"]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(build(args.output)))
