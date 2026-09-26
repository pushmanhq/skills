# Authorization, client setup, and updates

Read this only for installation, login/pairing, sender rename, logout, MCP setup,
or CLI updates. A request for one action doesn't authorize the others.

## Authorize an account CLI

- `pushman login` opens a browser for Google or Apple approval. It doesn't require
  the iPhone app during authorization; receiving pushes still requires the app.
- `pushman login --no-browser` prints a verification URL and user code for a
  headless or remote terminal. The user can approve on another device.
- `pushman pair` obtains approval in the signed-in iPhone app. It issues the same
  account-scoped CLI credential as login, not a credential restricted to that phone.

Start only the requested method. Show the short-lived user code and verification
URL only to the user, never public logs or issue reports. Let the user complete
provider sign-in and approval; never request their Google/Apple password. Never
expose the hidden device code or resulting bearer credential.

Browser launch failure doesn't mean the authorization failed: the CLI continues
polling and its printed URL remains usable. Don't restart a pending request or
automatically retry an expired, denied, or interrupted attempt. Let the CLI save
the credential, then verify with `pushman status`. No test send is implied.

If native credential storage fails, preserve the diagnostic and ask the user to
resolve access through the OS's normal UI. Don't export the keyring, weaken its
access controls, or work around the failure with a plaintext token file.

`pushman rename <nickname>` changes this sender's name. `pushman logout` revokes
and removes this CLI credential, potentially breaking dependent automations and
MCP clients. Run either only when explicitly requested and verify the resulting
status; don't log out just to diagnose a failure.

## Connect a local MCP client

The plugin itself is instruction-only. Don't alter an existing MCP configuration
merely because the skill was installed. When the user requests MCP setup, inspect
the client's configuration and reuse an existing Pushman entry where possible.

The server command is `pushman`, with arguments `mcp`. Supported CLI examples:

```sh
codex mcp add pushman -- pushman mcp
claude mcp add --scope user pushman -- pushman mcp
```

Use only the requested client's command. For a desktop client with a different
`PATH`, resolve the installed executable and configure its absolute path. Use the
client's supported settings, and don't put credentials in the configuration.

The client launches the stdio subprocess. Don't manually exchange JSON-RPC frames,
publish an HTTP endpoint, start a daemon, or create a tunnel. Verify initialization
and the seven tools listed in `SKILL.md` before claiming the connection works;
tool discovery doesn't authorize a send.

See the [official MCP guide](https://github.com/pushmanhq/pushman-cli/blob/main/docs/MCP.md)
for supported client configuration and transport details.

## Install or update the CLI

Use the [official installation guide](https://github.com/pushmanhq/pushman-cli/blob/main/docs/INSTALL.md)
and preserve the user's installation channel. Verify `pushman version` before and
after a requested update. Check installed `pushman self-update --help` first.

As of v0.1.1, `pushman self-update` only supports macOS/Linux executables owned by
the `whitekiwi/tap/pushman` Homebrew Formula. It verifies ownership before invoking
Homebrew and has no dry-run. Never bypass a refusal for a Go install, archive, or
development binary. Ask before changing channels or replacing an installation.

“Check for updates,” “update this skill,” and “update a notification by key” do not
authorize a binary update. An already-current result doesn't mean the version
changed. Updating the CLI doesn't authorize login, logout, a new MCP entry, or a
test notification.
