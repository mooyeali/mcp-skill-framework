# Design Document

## Overview

MCP Skill Framework is a Python framework for exposing pluggable skill tools
through a single MCP service. The framework keeps skill discovery, registration,
invocation, and transport concerns separate so the same tool set can be served
through MCP stdio or MCP streamable HTTP.

## Goals

- Provide one unified entry point for skill calls.
- Let skills be added or removed through local Python packages and `skills.yaml`.
- Support hot reload through the `reload_skills` MCP tool.
- Support both MCP stdio and MCP streamable HTTP transports.
- Keep the core service testable without starting an MCP process.

## Module Responsibilities

| Module | Responsibility |
| --- | --- |
| `mcp_skill_framework.__main__` | Parses CLI arguments and dispatches to the selected MCP transport. |
| `mcp_skill_framework.config` | Loads and validates `skills.yaml`. Resolves plugin directories relative to the config file. |
| `mcp_skill_framework.loader` | Imports enabled plugin modules and calls their `register(registry)` function. |
| `mcp_skill_framework.registry` | Stores skill definitions, rejects duplicate skill names, lists, describes, and invokes skills. |
| `mcp_skill_framework.models` | Defines the `SkillDefinition` data model and handler type. |
| `mcp_skill_framework.errors` | Defines framework-specific exceptions. |
| `mcp_skill_framework.server` | Builds the transport-neutral `SkillMcpService`, registers MCP tools with FastMCP, and runs stdio or streamable HTTP. |

## Architecture

```text
CLI
  |
  v
run_server(config, transport, host, port, path)
  |
  v
create_fastmcp_server(...)
  |
  +--> create_service(config)
  |      |
  |      +--> load_config(config)
  |      +--> SkillLoader(config).load_into(SkillRegistry())
  |
  +--> FastMCP tools
         - list_skills
         - describe_skill
         - call_skill
         - reload_skills
```

`SkillMcpService` is the core boundary. It does not know whether the caller is a
stdio client, a streamable HTTP client, or a direct unit test. Transport-specific
logic is limited to `create_fastmcp_server`, `run_stdio_server`, and
`run_streamable_http_server`.

## Skill Registration Flow

1. The CLI receives a config path.
2. `load_config` reads YAML and builds a `FrameworkConfig`.
3. `SkillLoader` adds the configured plugin directory to `sys.path`.
4. Enabled plugins are sorted by `(order, plugin_id)`.
5. Each plugin module is imported.
6. Each plugin's `register(registry)` function registers one or more tools.
7. The registry becomes the source of truth for listing, describing, and calling skills.

## Plugin Contract

A skill plugin is a Python package under the configured plugin directory. It must
expose a `register(registry)` function:

```python
def register(registry):
    registry.register(
        name="example.tool",
        description="Describe what this tool does.",
        input_schema={"type": "object"},
        handler=lambda arguments: {"ok": True},
    )
```

Handlers receive a `dict[str, Any]` and return JSON-serializable data.

## MCP Tools

The framework exposes these MCP tools:

| Tool | Purpose |
| --- | --- |
| `list_skills` | Returns skill names and descriptions. |
| `describe_skill` | Returns one skill's name, description, and input schema. |
| `call_skill` | Invokes a skill by name with an arguments object. |
| `reload_skills` | Reloads `skills.yaml`, imports enabled plugins, and replaces the active registry. |

## Transports

Two MCP transports are supported:

- `stdio`: process-based transport for local agents.
- `streamable-http`: HTTP MCP transport served at the configured path, default `/mcp`.

Both transports use the same FastMCP tool registration and the same
`SkillMcpService` instance. This keeps behavior consistent across clients.

## Hot Reload

`reload_skills` rebuilds a new `SkillRegistry` from the current config file and
swaps it into the running `SkillMcpService`. The loader invalidates import caches
and removes plugin modules from `sys.modules` before import, which lets newly
created or changed local plugin packages be loaded in a running service.

## Error Model

Framework exceptions are converted to structured MCP tool responses:

```json
{
  "error": {
    "type": "SkillNotFoundError",
    "message": "Skill not found: missing.tool"
  }
}
```

The current framework-specific errors are:

- `SkillFrameworkError`
- `SkillAlreadyRegisteredError`
- `SkillNotFoundError`
- `SkillLoadError`
- `SkillConfigError`

## Built-in Skills

| Skill | Description |
| --- | --- |
| `echo.echo` | Returns the provided text. |
| `local_files.list_directory` | Lists files and directories under a local path. |

## Test Coverage

The test suite covers:

- Config parsing and validation.
- Plugin loading, disabled plugins, and load error wrapping.
- Registry registration, duplicate detection, description, and invocation.
- Service-level list, describe, call, and reload behavior.
- CLI parser defaults and HTTP options.
- Real MCP stdio client integration.
- Real MCP streamable HTTP client integration.
