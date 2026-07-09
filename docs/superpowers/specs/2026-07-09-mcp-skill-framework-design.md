# MCP Skill Framework Design

## Goal

Build a Python MCP service framework that acts as the unified entry point for calling skill tools and supports pluggable skill modules.

## Scope

The first version provides a minimal but real framework:

- A Python package that can run an MCP server over stdio.
- A `SkillRegistry` that stores callable skill tools behind one stable interface.
- A `SkillLoader` that discovers plugins from a local `skills/` directory.
- A `skills.yaml` configuration file that enables, disables, aliases, and orders plugins.
- A sample `echo` skill plugin that proves the plugin contract.
- Tests for registry behavior, plugin loading, configuration filtering, and invocation.

HTTP/SSE transport, distributed plugin repositories, authentication, audit persistence, and hot reload are out of scope for the first version. The design leaves extension points for those features without implementing them early.

## Architecture

The framework is split into four layers:

1. MCP server adapter
   - Owns MCP-facing tool definitions.
   - Exposes the framework as one unified entry point through `list_skills`, `describe_skill`, and `call_skill`.
   - Delegates all business logic to the registry and loader.

2. Skill registry
   - Stores skill metadata and handlers.
   - Validates duplicate names.
   - Provides lookup, listing, description, and invocation APIs.

3. Plugin loader
   - Reads `skills.yaml`.
   - Discovers Python packages under the configured plugin directory.
   - Imports only enabled plugins.
   - Calls each plugin package's `register(registry)` function.

4. Skill plugins
   - Each plugin is a normal Python package.
   - Each plugin exposes `register(registry)`.
   - Plugins register one or more skill tools with names, descriptions, JSON-schema-like input schemas, and callables.

## Project Layout

```text
.
├── README.md
├── pyproject.toml
├── skills.yaml
├── src/
│   └── mcp_skill_framework/
│       ├── __init__.py
│       ├── __main__.py
│       ├── config.py
│       ├── errors.py
│       ├── loader.py
│       ├── models.py
│       ├── registry.py
│       └── server.py
├── skills/
│   └── echo/
│       └── __init__.py
└── tests/
    ├── test_config.py
    ├── test_loader.py
    ├── test_registry.py
    └── test_server.py
```

## Configuration

The default `skills.yaml` uses explicit configuration with directory discovery:

```yaml
plugin_dir: skills
plugins:
  echo:
    enabled: true
    module: echo
    order: 10
```

Rules:

- `plugin_dir` is resolved relative to the config file.
- Each plugin key is the local plugin id.
- `enabled: false` prevents import and registration.
- `module` defaults to the plugin key.
- `order` controls deterministic load order.

## Plugin Contract

A plugin must expose:

```python
def register(registry):
    registry.register(
        name="echo.echo",
        description="Return the provided text.",
        input_schema={
            "type": "object",
            "properties": {"text": {"type": "string"}},
            "required": ["text"],
        },
        handler=echo,
    )
```

Handlers receive a dictionary of arguments and return JSON-serializable data:

```python
def echo(arguments):
    return {"text": arguments["text"]}
```

## MCP Entry Points

The MCP service exposes these tools:

- `list_skills`: returns all registered skill names and descriptions.
- `describe_skill`: returns one skill's metadata and input schema.
- `call_skill`: invokes one skill by name with a JSON object of arguments.

The first version uses the official MCP Python SDK when available. The server adapter remains thin so the registry and loader can be tested without a running MCP transport.

## Error Handling

Framework errors are explicit:

- `SkillFrameworkError`: base class.
- `SkillAlreadyRegisteredError`: duplicate registration.
- `SkillNotFoundError`: missing skill invocation or description.
- `SkillLoadError`: plugin import or registration failure.
- `SkillConfigError`: invalid configuration file.

MCP-facing functions convert framework errors into structured error payloads rather than leaking tracebacks.

## Testing

Tests cover:

- Registering and listing skills.
- Rejecting duplicate registrations.
- Describing and invoking a registered skill.
- Loading enabled plugins from `skills.yaml`.
- Skipping disabled plugins.
- Wrapping import or registration errors as `SkillLoadError`.
- Calling the server adapter functions without starting an MCP process.

## Acceptance Criteria

- `python -m mcp_skill_framework --config skills.yaml` starts the MCP stdio server.
- `SkillRegistry` is the single in-process entry point for skill calls.
- Skills can be added by placing a package in `skills/` and enabling it in `skills.yaml`.
- The sample echo skill loads and can be called through the unified `call_skill` path.
- `pytest` passes for the registry, loader, config, and server adapter.
