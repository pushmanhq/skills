# Hosted ChatGPT and Codex plugin

The hosted distribution bundles the OAuth connection and the same maintained
Pushman skill. The local repo marketplace remains instruction-only for users
who prefer their installed CLI's stdio MCP. Neither package includes hooks,
installers, secrets or automatic notification sends.

Build the complete deterministic ZIP from the repository root:

```sh
python -m scripts.build_chatgpt --output /path/to/new/pushman-hosted-0.2.0.zip
```

The builder validates both distributions, refuses overwrite, and reads the ZIP
back to compare every file. The package contains root `plugin.json`, `mcp.json`,
the product icon and `skills/pushman/`. OAuth uses CIMD and server discovery,
with DCR available on the server. Keep the exact production URL stable.

Install an available Pushman hosted plugin, choose Connect, sign in through
Google or Apple, and review the requested access. No CLI installation or pasted
token is required. A receiving iPhone is still needed for delivery. Ask for a
usage or status read to verify the connection; installation does not authorize
a test notification.

## Publishing and updates

Upload the ZIP through the OpenAI plugin portal. Configure the verified publishing
identity, complete the exact domain challenge, connect OAuth, and inspect the
12 scanned tools and package findings. Keep credentials outside the public ZIP.
Review submission requires a dedicated test account/sample data, five positive
and three negative cases, and a walkthrough. Test them before submitting.
Approval and Publish are separate outcomes; a ZIP or personal plugin is not proof
of public-directory availability.

For package/skill changes, increase the aligned versions, rebuild a complete ZIP
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
