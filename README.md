<p align="center">
  <img src="https://raw.githubusercontent.com/pushmanhq/pushman/main/docs/assets/pushman-icon.png" alt="Pushman" width="112" height="112">
</p>

<h1 align="center">Pushman Skills</h1>

<p align="center">Your agent, one notification away.</p>

<p align="center">
  <a href="https://github.com/pushmanhq/skills/actions/workflows/validate.yml"><img alt="Validate" src="https://github.com/pushmanhq/skills/actions/workflows/validate.yml/badge.svg"></a>
  <a href="LICENSE"><img alt="MIT License" src="https://img.shields.io/badge/license-MIT-151515"></a>
  <a href="https://github.com/pushmanhq/skills/releases"><img alt="Release" src="https://img.shields.io/github/v/release/pushmanhq/skills"></a>
</p>

Official agent skill and plugins for [Pushman](https://github.com/pushmanhq/pushman).
Let Codex, Claude Code, and other skill-compatible agents send a notification to
your iPhone when you ask, inspect usage and history, or diagnose a delivery problem.

> [!NOTE]
> This integration is in beta. iPhone app availability is tracked in the
> [product repository](https://github.com/pushmanhq/pushman). Installing this skill
> does not install the app, authorize a CLI, or grant access to an account.

## Install

Install [Pushman CLI](https://github.com/pushmanhq/pushman-cli/blob/main/docs/INSTALL.md)
first (Homebrew on macOS/Linux):

```sh
brew install whitekiwi/tap/pushman
pushman version
```

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

Start a new agent session after installation. For skill-only installs, updates,
removal, and optional MCP setup, see [Installation](docs/INSTALL.md).

Authorize the CLI separately when ready:

```sh
pushman login
pushman status
```

Or use `pushman pair` to approve from the signed-in iPhone app. Browser login
doesn't require the app to authorize the CLI; receiving a notification still needs
an eligible iPhone with Pushman installed.

## Try it

Ask your agent:

> Use Pushman to show my remaining monthly allowance. Don't send anything.

> Use Pushman to notify all my eligible devices once with “Build finished”.

> My last Pushman send timed out. Inspect its status without resending.

The single [`pushman` skill](plugins/pushman/skills/pushman/SKILL.md) covers sending,
inspection, login/pairing guidance, local MCP setup, and eligible CLI updates.
It uses connected Pushman MCP tools when available and otherwise the installed CLI.
No MCP server, daemon, hook, or automatic installer is bundled.

## Safety by default

- Drafting, diagnostics, and installation never imply permission to send.
- An explicit send runs once; ambiguous results are not retried automatically.
- Omitting device targets means **all eligible receivers**.
- A successful send means server acceptance, not delivery or that you read it.
- Account credentials stay in the OS keyring. No tokens belong in chat or plugin configuration.

Skills guide agent behavior; they are not a security sandbox. Keep your client's
tool approvals enabled and review proposed external actions. Sending uses the same
hosted service and allowance as the CLI. Plugin installation is independent of
service pricing or account entitlement.

## Contribute and get help

Workflow bugs belong in [this repository's issues](https://github.com/pushmanhq/skills/issues).
For app or service help, use [Pushman support](https://app.pushman.whitekiwi.link/support/).
See [Contributing](CONTRIBUTING.md), [testing scenarios](docs/TESTING.md), and the
[security policy](SECURITY.md). Never attach unredacted notification history or credentials.

The skill definitions and packaging are [MIT licensed](LICENSE), independently
of the hosted service, iPhone app, and trademarks. Packaging follows the
[c6s skills](https://github.com/c6shq/skills) repository's dual-marketplace approach.
