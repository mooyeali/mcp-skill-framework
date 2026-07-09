# 使用文档

## 环境要求

- Python 3.11 或更高版本。
- `pip`。
- 如需运行 MCP transport，需要安装 MCP SDK 可选依赖。

## 开发安装

```bash
pip install -e ".[test,mcp]"
```

运行测试：

```bash
pytest -v
```

查看 CLI 帮助：

```bash
python -m mcp_skill_framework --help
```

## 启动 MCP Stdio 服务

stdio 适用于由本地 MCP agent 直接启动服务进程的场景：

```bash
python -m mcp_skill_framework --transport stdio --config skills.yaml
```

`stdio` 是默认 transport，因此下面的命令等价：

```bash
python -m mcp_skill_framework --config skills.yaml
```

## 启动 MCP Streamable HTTP 服务

streamable HTTP 适用于通过 HTTP 连接的 agent：

```bash
python -m mcp_skill_framework \
  --transport streamable-http \
  --host 127.0.0.1 \
  --port 8000 \
  --path /mcp \
  --config skills.yaml
```

默认访问地址：

```text
http://127.0.0.1:8000/mcp
```

## 可用 MCP 工具

### `list_skills`

返回所有已注册 skill 的名称和描述。

示例响应：

```json
{
  "skills": [
    {"name": "echo.echo", "description": "Return the provided text."}
  ]
}
```

### `describe_skill`

返回指定 skill 的元数据和输入 schema。

参数：

```json
{"name": "echo.echo"}
```

### `call_skill`

调用已注册的 skill。

参数：

```json
{
  "name": "echo.echo",
  "arguments": {"text": "hello"}
}
```

响应：

```json
{"result": {"text": "hello"}}
```

### `reload_skills`

重新读取 `skills.yaml`，导入已启用插件，并替换当前 registry。

参数：

```json
{}
```

响应：

```json
{
  "reloaded": true,
  "skills": [
    {"name": "echo.echo", "description": "Return the provided text."}
  ]
}
```

## 内置 Skills

### `echo.echo`

返回传入文本。

```json
{
  "name": "echo.echo",
  "arguments": {"text": "hello"}
}
```

### `local_files.list_directory`

列出本地目录内容。

```json
{
  "name": "local_files.list_directory",
  "arguments": {
    "path": ".",
    "include_hidden": false
  }
}
```

每个条目包含：

- `name`
- `path`
- `type`：`file` 或 `directory`
- `size`：文件大小，目录为 `null`

## 新增 Skill

在 `skills/` 下创建 Python 包：

```text
skills/
  my_skill/
    __init__.py
```

插件示例：

```python
def register(registry):
    registry.register(
        name="my_skill.ping",
        description="Return pong.",
        input_schema={"type": "object"},
        handler=lambda arguments: {"pong": True},
    )
```

在 `skills.yaml` 中启用：

```yaml
plugins:
  my_skill:
    enabled: true
    module: my_skill
    order: 30
```

通过 MCP 调用 `reload_skills` 工具热加载：

```json
{}
```

## 错误响应

框架错误会以结构化对象返回：

```json
{
  "error": {
    "type": "SkillNotFoundError",
    "message": "Skill not found: missing.tool"
  }
}
```

## 已验证行为

仓库测试覆盖：

- MCP stdio 启动和热插拔 reload。
- MCP streamable HTTP 启动和 skill 调用。
- 不启动 transport 的 service 直接调用。
