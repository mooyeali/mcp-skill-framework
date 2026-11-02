# 配置文档

## 配置文件

框架读取 YAML 配置文件，通常为 `skills.yaml`。

默认配置：

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

## 顶层字段

| 字段 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `plugin_dir` | string | `skills` | 插件包所在目录。相对路径按配置文件所在目录解析。 |
| `plugins` | mapping | `{}` | 插件配置，以 plugin id 作为 key。 |

YAML 根节点必须是 mapping。如果 `plugin_dir` 不是字符串，或 `plugins` 不是
mapping，配置加载会抛出 `SkillConfigError`。

## 插件字段

`plugins` 下每个条目的结构如下：

```yaml
plugins:
  plugin_id:
    enabled: true
    module: plugin_module
    order: 100
```

| 字段 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `enabled` | boolean | `true` | 是否导入并注册插件。禁用插件会被跳过。 |
| `module` | string | plugin id | 从 `plugin_dir` 中导入的 Python 模块名。 |
| `order` | integer | `100` | 加载顺序。已启用插件按 `(order, plugin_id)` 排序。 |

plugin id 必须是字符串。每个插件配置必须是 mapping。字段类型错误会抛出
`SkillConfigError`。

## 路径解析

`plugin_dir` 按配置文件路径解析，而不是按当前 shell 目录解析。

示例：

```text
/opt/app/config/skills.yaml
/opt/app/config/my_skills/
```

```yaml
plugin_dir: my_skills
```

解析后的插件目录是 `/opt/app/config/my_skills`。

## 加载行为

服务启动时：

1. `load_config` 读取并校验 YAML。
2. `SkillLoader` 临时将 `plugin_dir` 加入 `sys.path`。
3. 按确定性顺序导入已启用插件。
4. 调用每个插件的 `register(registry)` 函数。
5. 如果 loader 自己插入了插件目录，会在结束后从 `sys.path` 移除。

reload 时，loader 会失效 import cache，并在导入前从 `sys.modules` 移除插件模块。
因此 `reload_skills` 可以让运行中的服务识别本地插件变更。

## CLI 选项

```bash
python -m mcp_skill_framework \
  --config skills.yaml \
  --transport stdio \
  --host 127.0.0.1 \
  --port 8000 \
  --path /mcp
```

| 选项 | 默认值 | 说明 |
| --- | --- | --- |
| `--config` | `skills.yaml` | YAML 配置文件路径。 |
| `--transport` | `stdio` | MCP transport。支持：`stdio`、`streamable-http`。 |
| `--host` | `127.0.0.1` | `streamable-http` 使用的监听地址。 |
| `--port` | `8000` | `streamable-http` 使用的端口。 |
| `--path` | `/mcp` | `streamable-http` 使用的 HTTP 路径。 |

`--host`、`--port`、`--path` 仅对 `streamable-http` 生效。

HTTP MCP client 的 agent 配置：

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

已启用插件中的 skill 会直接暴露为 MCP 工具。`list_skills`、`describe_skill`
和 `call_skill` 等兼容辅助工具仍然保留。

## 内置插件配置

### Echo

```yaml
echo:
  enabled: true
  module: echo
  order: 10
```

注册：

- `echo.echo`

### Local Files

```yaml
local_files:
  enabled: true
  module: local_files
  order: 20
```

注册：

- `local_files.list_directory`

## 常见配置任务

### 禁用插件

```yaml
plugins:
  local_files:
    enabled: false
```

禁用插件不会被导入。

### 添加新插件

```yaml
plugin_dir: skills
plugins:
  my_skill:
    enabled: true
    module: my_skill
    order: 30
```

插件包必须存在于：

```text
skills/my_skill/__init__.py
```

### 指定插件加载顺序

使用 `order`：

```yaml
plugins:
  first:
    enabled: true
    order: 10
  second:
    enabled: true
    order: 20
```

如果两个插件的 order 相同，会使用 `plugin_id` 作为排序补充条件。

## 错误场景

| 场景 | 错误 |
| --- | --- |
| 配置文件不可读 | `SkillConfigError` |
| YAML 格式非法 | `SkillConfigError` |
| 根节点不是 mapping | `SkillConfigError` |
| `plugin_dir` 不是字符串 | `SkillConfigError` |
| `plugins` 不是 mapping | `SkillConfigError` |
| 插件导入或注册失败 | `SkillLoadError` |
| 多个插件注册相同 skill 名称 | 加载阶段会以 `SkillLoadError` 包装 `SkillAlreadyRegisteredError` |
