# Contributing

Keep the skill small, portable, and consistent with released
[Pushman CLI behavior](https://github.com/pushmanhq/pushman-cli).
New commands or product features belong in the CLI/product repositories first.
Please keep discussions respectful and reports free of private data.

## Validate locally

Python 3.11+ is needed only for repository checks, not for using the plugin:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python scripts/validate.py
.venv/bin/python -m unittest discover -s tests -v
```

If Claude Code is installed, also run:

```sh
claude plugin validate .
claude plugin validate plugins/pushman
```

Automated checks validate structure, references, version alignment, and the
instruction-only package boundary. They don't prove agent behavior. For behavior
changes, record the relevant [manual scenarios](docs/TESTING.md) in your PR,
including anything not tested. Use synthetic data and mock tools; live account
operations need separate authorization.

## Publishing

Keep the version aligned in both plugin manifests and the Claude marketplace
entry. Update all three for a new plugin release; this version is independent of
the CLI. Require validation on the release commit before tagging `vX.Y.Z`.

Never add hooks, automatic login, test notifications, embedded tokens, or a
bundled MCP entry as an incidental packaging change. Link to public documentation,
not private product repositories or a maintainer's machine.
