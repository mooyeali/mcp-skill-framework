# MCP Stdio and HTTP Transport Design

## Goal

Update the MCP skill framework so the same skill registry and MCP tools can be
served through both MCP stdio and MCP HTTP.

## Protocol Decision

HTTP support uses the MCP SDK `streamable-http` transport, not a custom REST API.
This keeps the framework compatible with MCP clients that speak the MCP HTTP
protocol at an endpoint such as `http://127.0.0.1:8000/mcp`.

## Current State

The framework currently exposes MCP tools through stdio only:

- `python -m mcp_skill_framework --config skills.yaml`
- `run_stdio_server(config_path)`
- MCP tools:
  - `list_skills`
  - `describe_skill`
  - `call_skill`
  - `reload_skills`

The service core is already transport-neutral through `SkillMcpService`, so the
transport work should stay in the server adapter and CLI.

## Target CLI

```bash
python -m mcp_skill_framework --transport stdio --config skills.yaml
python -m mcp_skill_framework --transport streamable-http --host 127.0.0.1 --port 8000 --path /mcp --config skills.yaml
```

Defaults:

- `--transport stdio`
- `--host 127.0.0.1`
- `--port 8000`
- `--path /mcp`

## Architecture

Add a shared FastMCP factory:

```python
create_fastmcp_server(config_path, host="127.0.0.1", port=8000, path="/mcp")
```

The factory:

- Creates `SkillMcpService`.
- Creates `FastMCP("mcp-skill-framework", host=host, port=port, streamable_http_path=path)`.
- Registers the same tools for every transport.

Transport runners:

- `run_stdio_server(config_path)` calls `mcp.run(transport="stdio")`.
- `run_streamable_http_server(config_path, host, port, path)` calls
  `mcp.run(transport="streamable-http")`.
- `run_server(config_path, transport, host, port, path)` dispatches between the
  two supported transports.

## Testing

Keep existing stdio coverage and add HTTP coverage:

- CLI parser test verifies transport, host, port, and path arguments.
- Stdio integration test continues to start `python -m mcp_skill_framework`.
- Streamable HTTP integration test starts the CLI as a subprocess with
  `--transport streamable-http`, connects with
  `mcp.client.streamable_http.streamablehttp_client`, initializes
  `ClientSession`, and calls `list_skills` and `call_skill`.

## Acceptance Criteria

- Stdio MCP clients can still connect and call existing tools.
- Streamable HTTP MCP clients can connect to `/mcp` and call the same tools.
- `reload_skills` remains available through both transports.
- `pytest -v` passes.
- README documents both transport modes.
