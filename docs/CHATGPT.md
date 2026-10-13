# Hosted ChatGPT and Codex plugin

Use a registered ChatGPT app when users should see an **App** and **Connected
accounts** card, as with other OAuth integrations. A portable ZIP that bundles
`mcp.json` alone is a different integration: it appears as an **MCP server** in a
local client. A personal ZIP import does not register a cloud app. Updating its
skill version cannot add a registered-app account card.

The local repo marketplace remains instruction-only for CLI users. The portable
hosted package supports direct MCP clients and the public **With MCP** submission
flow. A private connected package references an existing registered ChatGPT app.
All use the same maintained skill and include no hooks, installers, secrets or
automatic notification sends.

## Registered app and personal plugin

In ChatGPT Plugins, choose **Add custom MCP server** and register
`https://app.pushman.whitekiwi.link/mcp` with OAuth and discovery/dynamic client
registration. Reuse an existing Pushman registration when present. Review the
risk notice and choose **Create as a plugin**. The technical page ID starts with
`plugin_asdk_app_`; the app ID in `.app.json` starts with `asdk_app_`.

Complete Google or Apple sign-in and access approval through that app's Connect
flow. Verify the connected account, scan the 12 hosted tools, and perform an
authorized status/usage read. The registered app uses no local CLI or pasted
token. A receiving iPhone is still needed for delivery. Installation and OAuth
do not authorize a test notification.

Download the existing registered plugin ZIP to obtain its exact manifest `name`
and `.app.json` ID. Build a complete connected ZIP outside this public checkout:

```sh
python -m scripts.build_connected \
  --app-id "$PUSHMAN_REGISTERED_APP_ID" \
  --plugin-name "$PUSHMAN_REGISTERED_PLUGIN_NAME" \
  --version "$PUSHMAN_CONNECTED_VERSION" \
  --output /path/to/new/pushman-connected.zip
```

The builder preserves the supplied registration name and creates an ID-only
`.app.json` mapping, the icon and complete skill. It adds no bundled MCP server
and does not install or connect anything. Keep real private registration IDs
and generated connected ZIPs out of public Git and releases. Increase the wrapper
version from its existing registration; it is independent of the maintained skill version.

Use **Upload new version** on that same registered plugin, then download the
updated ZIP and compare all file contents. Verify the installed cache, connected
account and actual tool calls separately. Preserve the registration and OAuth
connection when updating skills. Only remove an older standalone duplicate when
the user requests its removal.

## Portable MCP package

Build the complete deterministic ZIP from the repository root:

```sh
python -m scripts.build_chatgpt --output /path/to/new/pushman-hosted-0.2.2.zip
```

The builder validates both distributions, refuses overwrite, and reads the ZIP
back to compare every file. The package contains root `plugin.json`, `mcp.json`,
the product icon and `skills/pushman/`. OAuth uses CIMD and server discovery,
with DCR available on the server. Keep the exact production URL stable.

Direct MCP clients manage this package's OAuth connection in their own MCP
settings. Its local MCP gear is distinct from ChatGPT's registered-app account
card. Use the registered-app procedure above for a personal ChatGPT app.

## Publishing and updates

For public distribution, upload the portable ZIP through the OpenAI plugin portal
and use **With MCP** for the HTTPS endpoint. Configure the verified publishing
identity, complete the exact domain challenge, connect OAuth, and inspect the
12 scanned tools and package findings. Keep credentials outside the public ZIP.
Review submission requires a dedicated test account/sample data, five positive
and three negative cases, and a walkthrough. Test them before submitting.
Approval and Publish are separate outcomes; a ZIP or personal plugin is not proof
of public-directory availability.

For public package/skill changes, increase the aligned versions, rebuild a complete ZIP
and upload a new version to the same plugin. For hosted tool changes, deploy to
the existing URL and verify the applicable scan. Do not rely on public plugins'
daily scans for a development/personal connection. Do not create a replacement
plugin just to update skills.

## Review scenarios

| Prompt | Expected operation/result |
| --- | --- |
| Show my monthly usage without sending. | `pushman_get_usage`; no send. |
| List my receiving devices. | `pushman_list_devices`; eligibility, no send. |
| Show this sender's retained history. | `pushman_list_history`; follow needed `nextCursor`, no other sender data. |
| Rename this sender to Review. | `pushman_rename_sender`; only current sender changes. |
| Send the specified sample notification once to the named sample iPhone. | One `pushman_send_notification`; acceptance ID/count, no retry or delivery claim. |
| Draft a notification; do not send it. | Draft only, no send. |
| A submitted send times out. | Explain unknown outcome; no automatic retry. |
| Show another account's message or use a send-only token for history. | Refuse missing authority; never expose or copy credentials. |

The send scenario requires its own explicit authorization and a dedicated sample
receiver. Automated package validation uses synthetic fixtures and does not run
these scenarios on a live account.

Sources: [plugin packaging](https://developers.openai.com/plugins/build/plugins),
[OAuth requirements](https://developers.openai.com/plugins/build/auth),
[submission and updates](https://developers.openai.com/plugins/deploy/submission).
