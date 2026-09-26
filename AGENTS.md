# Agent guidance

- This public repository distributes Pushman's agent skill and plugin manifests, not product implementation or private operations.
- Treat the released CLI help and public docs in `pushmanhq/pushman-cli` as the capability contract. Never invent commands, flags, plans, or API behavior.
- Preserve explicit send intent, account credential boundaries, and no automatic retry of ambiguous sends. Skill installation is not permission to log in, change client configuration, or send a test notification.
- Do not include real credentials, notification content, device names, account identifiers, private logs, or machine-specific paths.
- Keep Codex, Claude Code, and marketplace plugin versions aligned. Keep the package instruction-only: no hooks, bundled MCP configuration, or automatic installers.
- Run `python scripts/validate.py` and `python -m unittest discover -s tests -v` with `requirements-dev.txt` installed. Use the manual scenarios in `docs/TESTING.md` for behavior changes; never exercise a live send without authorization.
- Inspect staged and unstaged changes before committing. Commit messages use `{type}: {imperative message}` with a lowercase type.
