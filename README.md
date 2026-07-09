# MCP Skill Framework

Python MCP service framework for exposing pluggable skill tools through one unified entry point.

## Quickstart

```bash
pip install -e ".[test]"
pytest -v
python -m mcp_skill_framework --help
```

Run the stdio MCP server after installing the optional MCP SDK:

```bash
pip install -e ".[mcp]"
python -m mcp_skill_framework --config skills.yaml
```

## Configuration

`skills.yaml` enables local skill plugins:

```yaml
plugin_dir: skills
plugins:
  echo:
    enabled: true
    module: echo
    order: 10
```

`plugin_dir` is resolved relative to the config file. Disabled plugins are not imported.

## Plugin Contract

Each plugin is a Python package with a `register(registry)` function:

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
        handler=lambda arguments: {"text": arguments["text"]},
    )
```

Handlers receive a dictionary and return JSON-serializable data.

## Unified Entry Points

The framework exposes these MCP-facing operations:

- `list_skills`
- `describe_skill`
- `call_skill`
