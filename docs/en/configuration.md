# Configuration Reference

## Configuration File

The framework reads a YAML file, usually `skills.yaml`.

Default:

```yaml
plugin_dir: skills
plugins:
  echo:
    enabled: true
    module: echo
    order: 10
  local_files:
    enabled: true
    module: local_files
    order: 20
```

## Top-level Fields

| Field | Type | Default | Description |
| --- | --- | --- | --- |
| `plugin_dir` | string | `skills` | Directory containing plugin packages. Relative paths are resolved relative to the config file. |
| `plugins` | mapping | `{}` | Plugin configuration keyed by plugin id. |

The root YAML value must be a mapping. If `plugin_dir` is not a string or
`plugins` is not a mapping, config loading fails with `SkillConfigError`.

## Plugin Fields

Each entry under `plugins` has this shape:

```yaml
plugins:
  plugin_id:
    enabled: true
    module: plugin_module
    order: 100
```

| Field | Type | Default | Description |
| --- | --- | --- | --- |
| `enabled` | boolean | `true` | Whether the plugin is imported and registered. Disabled plugins are skipped. |
| `module` | string | plugin id | Python module name to import from `plugin_dir`. |
| `order` | integer | `100` | Load order. Enabled plugins are sorted by `(order, plugin_id)`. |

Plugin ids must be strings. Each plugin config must be a mapping. Invalid field
types fail with `SkillConfigError`.

## Path Resolution

`plugin_dir` is resolved relative to the config file path, not relative to the
current shell directory.

Example:

```text
/opt/app/config/skills.yaml
/opt/app/config/my_skills/
```

```yaml
plugin_dir: my_skills
```

The resolved plugin directory is `/opt/app/config/my_skills`.

## Loading Behavior

When the service starts:

1. `load_config` reads and validates the YAML.
2. `SkillLoader` temporarily adds `plugin_dir` to `sys.path`.
3. Enabled plugins are imported in deterministic order.
4. Each plugin's `register(registry)` function is called.
5. The plugin directory is removed from `sys.path` if the loader inserted it.

During reload, import caches are invalidated and plugin modules are removed from
`sys.modules` before import. This lets local plugin changes be picked up by
`reload_skills`.

## CLI Options

```bash
python -m mcp_skill_framework \
  --config skills.yaml \
  --transport stdio \
  --host 127.0.0.1 \
  --port 8000 \
  --path /mcp
```

| Option | Default | Description |
| --- | --- | --- |
| `--config` | `skills.yaml` | Path to the YAML configuration file. |
| `--transport` | `stdio` | MCP transport. Supported values: `stdio`, `streamable-http`. |
| `--host` | `127.0.0.1` | Host for `streamable-http`. |
| `--port` | `8000` | Port for `streamable-http`. |
| `--path` | `/mcp` | HTTP path for `streamable-http`. |

`--host`, `--port`, and `--path` are only used by `streamable-http`.

Agent configuration for HTTP MCP clients:

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

Enabled plugin skills are exposed as direct MCP tools. Compatibility helpers
such as `list_skills`, `describe_skill`, and `call_skill` remain available.

## Built-in Plugin Configuration

### Echo

```yaml
echo:
  enabled: true
  module: echo
  order: 10
```

Registers:

- `echo.echo`

### Local Files

```yaml
local_files:
  enabled: true
  module: local_files
  order: 20
```

Registers:

- `local_files.list_directory`

## Common Configuration Tasks

### Disable a Plugin

```yaml
plugins:
  local_files:
    enabled: false
```

Disabled plugins are not imported.

### Add a New Plugin

```yaml
plugin_dir: skills
plugins:
  my_skill:
    enabled: true
    module: my_skill
    order: 30
```

The package must exist at:

```text
skills/my_skill/__init__.py
```

### Load Plugins in a Specific Order

Use `order`:

```yaml
plugins:
  first:
    enabled: true
    order: 10
  second:
    enabled: true
    order: 20
```

If two plugins have the same order, `plugin_id` is used as a tie-breaker.

## Error Cases

| Case | Error |
| --- | --- |
| Config file cannot be read | `SkillConfigError` |
| YAML is invalid | `SkillConfigError` |
| Root value is not a mapping | `SkillConfigError` |
| `plugin_dir` is not a string | `SkillConfigError` |
| `plugins` is not a mapping | `SkillConfigError` |
| Plugin import or registration fails | `SkillLoadError` |
| Two plugins register the same skill name | `SkillAlreadyRegisteredError` wrapped by `SkillLoadError` during loading |
