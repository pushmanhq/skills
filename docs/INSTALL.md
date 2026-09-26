# Installation and maintenance

The plugin requires an installed [Pushman CLI](https://github.com/pushmanhq/pushman-cli/blob/main/docs/INSTALL.md).
CLI v0.1.1 is the verified baseline. Use a compatible host with plugin support;
check its installed `plugin --help` if a command is unavailable.

## Plugin install

### Codex

```sh
codex plugin marketplace add pushmanhq/skills
codex plugin add pushman@pushman-skills
```

### Claude Code

```sh
claude plugin marketplace add pushmanhq/skills
claude plugin install pushman@pushman-skills
```

Start a new session so it can discover the skill. Installation does not modify
Pushman authorization, send notifications, or configure an MCP server. The
marketplace authentication policy is host metadata, not an automatic Pushman login.

If you already have a personal `pushman` skill, choose one copy. Don't overwrite
custom instructions blindly; compare them before disabling a duplicate.

## Skill-only clients

The portable skill lives at
[`plugins/pushman/skills/pushman`](../plugins/pushman/skills/pushman/SKILL.md).
Clone this repository and use your client's supported skill importer, including
the entire directory (especially `references/`). No plugin manifests or Python
dependencies are needed to use the skill itself.

```sh
git clone https://github.com/pushmanhq/skills.git pushman-skills
```

Refer to your client's skill-installation documentation for its location and
scope. Don't overwrite an existing skill with the same name without reviewing it.

## Optional MCP connection

CLI fallback works without MCP. If you want typed tools, authorize with
`pushman login` or `pushman pair`, then explicitly configure your chosen client
using the [MCP guide](https://github.com/pushmanhq/pushman-cli/blob/main/docs/MCP.md).
This package does not bundle an MCP entry, so it won't start a duplicate of an
existing `pushman mcp` server. Never put tokens into agent configuration.

## Update or remove

Plugin versions and CLI versions are independent. Refresh the marketplace and
update through your client's plugin manager, then start a new session. See
`codex plugin marketplace upgrade --help`, `codex plugin add --help`, or
`claude plugin update --help` for your installed client's update options.

Remove just the plugin:

```sh
codex plugin remove pushman@pushman-skills
# or
claude plugin uninstall pushman@pushman-skills
```

Removing a skill/plugin doesn't revoke the Pushman CLI credential, uninstall the
CLI, or remove a separately configured MCP entry. Run `pushman logout` only when
you intend to revoke that CLI's access. Likewise, `pushman self-update` updates
an eligible Homebrew CLI, not this plugin.
