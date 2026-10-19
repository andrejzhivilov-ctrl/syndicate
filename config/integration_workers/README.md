# Per-agent integration worker examples

These JSON files are **deployment templates only**. They are not read by the application automatically, are not Vault policies, and have not been applied to any worker. Replace the worker API key only in a private operator-controlled file before storing it in the corresponding Vault path; never commit filled secrets.

## Prepared, bounded grants

- `kodex.example.json`: skills list/read, review-only knowledge-pool search/read for KODEX, and local MCP-pool search/read for KODEX.
- `architect.example.json`: skills list/read and local MCP-pool search/read for Architect.
- `marshal.example.json`: skills list/read, review-only knowledge-pool search/read for Marshal, and local MCP-pool search/read for Marshal.

The MCP server map is empty in every template. There is no `mcp.list` or `mcp.call`, server launch, package installation, external account access, or shared knowledge-pool access. MCP catalog descriptions remain untrusted. Knowledge and MCP pool handlers also require the matching per-agent allowlists shown in each file.

Agent profiles remain `prepared_not_enabled`; these templates do not activate an agent runtime, create Vault policies, add worker credentials, or make live calls. The generic `config/integration_worker.example.json` remains default-deny for the knowledge and MCP pools. All other proposals for unimplemented capabilities remain proposals until their handlers, scopes, tests, and operator approval exist.
