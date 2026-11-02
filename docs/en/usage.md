# Usage Guide

## Requirements

- Python 3.11 or newer.
- `pip`.
- Optional MCP SDK extras for running MCP transports.

## Install for Development

```bash
pip install -e ".[test,mcp]"
```

Run the test suite:

```bash
pytest -v
```

Show CLI help:

```bash
python -m mcp_skill_framework --help
```

## Start the MCP Stdio Server

Use stdio for local MCP agents that launch the server process directly:

```bash
python -m mcp_skill_framework --transport stdio --config skills.yaml
```

`stdio` is the default transport, so this equivalent command also works:

```bash
python -m mcp_skill_framework --config skills.yaml
```

## Start the MCP Streamable HTTP Server

Use streamable HTTP for agents that connect over HTTP:

```bash
python -m mcp_skill_framework \
  --transport streamable-http \
  --host 127.0.0.1 \
  --port 8000 \
  --path /mcp \
  --config skills.yaml
```

The default endpoint is:

```text
http://127.0.0.1:8000/mcp
```

## Run with Docker

Build the image:

```bash
docker build -t mcp-skill-framework:local .
```

Export the built image:

```bash
mkdir -p dist
docker save mcp-skill-framework:local -o dist/mcp-skill-framework-local.tar
```

Import the exported image:

```bash
./scripts/import-docker-image.sh dist/mcp-skill-framework-local.tar
```

Run it with the host `skills` directory mounted into the container:

```bash
docker run --rm -p 8000:8000 -v "$PWD/skills:/app/skills:ro" mcp-skill-framework:local
```

The image starts the streamable HTTP server by default. Its default config is
`/app/skills.yaml`, and that config reads plugins from `/app/skills`.

Generic agent configuration:

```json
{
  "mcpServers": {
    "skills": {
      "type": "streamable-http",
      "url": "http://127.0.0.1:8000/mcp"
    }
  }
}
```

## Available MCP Tools

Enabled skills are exposed directly as MCP tools. Agents should call tool names
such as `echo.echo` or `local_files.list_directory` directly.

The framework also keeps compatibility and management tools:

### `list_skills`

Returns all registered skill names and descriptions.

Example response:

```json
{
  "skills": [
    {"name": "echo.echo", "description": "Return the provided text."}
  ]
}
```

### `describe_skill`

Returns one skill's metadata and input schema.

Arguments:

```json
{"name": "echo.echo"}
```

### `call_skill`

Compatibility helper that invokes a registered skill by name. Prefer direct
tool calls for agent integrations.

Arguments:

```json
{
  "name": "echo.echo",
  "arguments": {"text": "hello"}
}
```

Response:

```json
{"result": {"text": "hello"}}
```

### `reload_skills`

Reloads `skills.yaml`, imports enabled plugins, and replaces the active registry.

Arguments:

```json
{}
```

Response:

```json
{
  "reloaded": true,
  "skills": [
    {"name": "echo.echo", "description": "Return the provided text."}
  ]
}
```

## Built-in Skills

### `echo.echo`

Returns the provided text.

```json
{
  "text": "hello"
}
```

### `local_files.list_directory`

Lists entries in a local directory.

```json
{
  "path": ".",
  "include_hidden": false
}
```

Each entry includes:

- `name`
- `path`
- `type`: `file` or `directory`
- `size`: file size in bytes, or `null` for directories

## Add a New Skill

Create a Python package under `skills/`:

```text
skills/
  my_skill/
    __init__.py
```

Example plugin:

```python
def register(registry):
    registry.register(
        name="my_skill.ping",
        description="Return pong.",
        input_schema={"type": "object"},
        handler=lambda arguments: {"pong": True},
    )
```

Enable it in `skills.yaml`:

```yaml
plugins:
  my_skill:
    enabled: true
    module: my_skill
    order: 30
```

Reload the running service through MCP:

```json
{}
```

using the `reload_skills` tool.

## Error Responses

Framework errors are returned as structured objects:

```json
{
  "error": {
    "type": "SkillNotFoundError",
    "message": "Skill not found: missing.tool"
  }
}
```

## Test Verified Behavior

The repository includes integration tests for:

- MCP stdio startup and hot-plug reload.
- MCP streamable HTTP startup and skill calls.
- Direct service calls without starting a transport.
