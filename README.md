# MCP Skill Framework

Python MCP service framework for exposing pluggable skill tools through one
unified entry point. The framework supports both MCP stdio and MCP streamable
HTTP transports.

## Documentation

English:

- [Design](docs/en/design.md)
- [Usage](docs/en/usage.md)
- [Configuration](docs/en/configuration.md)

Chinese:

- [设计文档](docs/zh/design.md)
- [使用文档](docs/zh/usage.md)
- [配置文档](docs/zh/configuration.md)

## Quickstart

```bash
pip install -e ".[test,mcp]"
pytest -v
python -m mcp_skill_framework --help
```

Run with MCP stdio:

```bash
python -m mcp_skill_framework --transport stdio --config skills.yaml
```

Run with MCP streamable HTTP:

```bash
python -m mcp_skill_framework --transport streamable-http --host 127.0.0.1 --port 8000 --path /mcp --config skills.yaml
```

Default HTTP endpoint:

```text
http://127.0.0.1:8000/mcp
```

## Built-in Skills

- `echo.echo`: returns the provided text.
- `local_files.list_directory`: lists files and directories under a local path.

## MCP Tools

- `list_skills`: list registered skill names and descriptions.
- `describe_skill`: return one skill's metadata and input schema.
- `call_skill`: invoke one skill with an arguments object.
- `reload_skills`: reload `skills.yaml` and enabled plugin modules without
  restarting the service.

## Project Layout

```text
src/mcp_skill_framework/   Framework package
skills/                    Local plugin packages
tests/                     Unit and MCP integration tests
docs/en/                   English documentation
docs/zh/                   Chinese documentation
skills.yaml                Default plugin configuration
```

---

# MCP Skill Framework 中文说明

MCP Skill Framework 是一个 Python MCP 服务框架，用于通过统一入口暴露可插拔
skill 工具。框架同时支持 MCP stdio 和 MCP streamable HTTP 两种传输协议。

## 文档

中文：

- [设计文档](docs/zh/design.md)
- [使用文档](docs/zh/usage.md)
- [配置文档](docs/zh/configuration.md)

English:

- [Design](docs/en/design.md)
- [Usage](docs/en/usage.md)
- [Configuration](docs/en/configuration.md)

## 快速开始

```bash
pip install -e ".[test,mcp]"
pytest -v
python -m mcp_skill_framework --help
```

使用 MCP stdio 启动：

```bash
python -m mcp_skill_framework --transport stdio --config skills.yaml
```

使用 MCP streamable HTTP 启动：

```bash
python -m mcp_skill_framework --transport streamable-http --host 127.0.0.1 --port 8000 --path /mcp --config skills.yaml
```

默认 HTTP 端点：

```text
http://127.0.0.1:8000/mcp
```

## 内置 Skills

- `echo.echo`：返回输入文本。
- `local_files.list_directory`：列出本地路径下的文件和目录。

## MCP 工具

- `list_skills`：列出已注册 skill 的名称和描述。
- `describe_skill`：返回指定 skill 的元数据和输入 schema。
- `call_skill`：使用参数对象调用指定 skill。
- `reload_skills`：在不重启服务的情况下重新加载 `skills.yaml` 和已启用插件。

## 项目结构

```text
src/mcp_skill_framework/   框架包
skills/                    本地插件包
tests/                     单元测试和 MCP 集成测试
docs/en/                   英文文档
docs/zh/                   中文文档
skills.yaml                默认插件配置
```
