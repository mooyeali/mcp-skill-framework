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

Build a local Docker image:

```bash
docker build -t mcp-skill-framework:local .
```

Export the built image to a tar file:

```bash
mkdir -p dist
docker save mcp-skill-framework:local -o dist/mcp-skill-framework-local.tar
```

Import the exported image on another machine:

```bash
./scripts/import-docker-image.sh dist/mcp-skill-framework-local.tar
```

Run the image with the host `skills` folder mounted as the default skill source:

```bash
docker run --rm -p 8000:8000 -v "$PWD/skills:/app/skills:ro" mcp-skill-framework:local
```

The container starts the streamable HTTP server by default and reads plugins
from `/app/skills`, which should normally be mounted from the host.

## Built-in Skills

- `echo.echo`: returns the provided text.
- `local_files.list_directory`: lists files and directories under a local path.

## MCP Tools

Enabled skills are exposed directly as MCP tools. For example, agents can call
`echo.echo` and `local_files.list_directory` without going through `call_skill`.

- `echo.echo`: direct skill tool.
- `local_files.list_directory`: direct skill tool.
- `list_skills`: compatibility helper that lists registered skill names and
  descriptions.
- `describe_skill`: compatibility helper that returns one skill's metadata and
  input schema.
- `call_skill`: compatibility helper that invokes one skill with an arguments
  object.
- `reload_skills`: reload `skills.yaml` and enabled plugin modules without
  restarting the service. Newly loaded skills are synced into the MCP tool list.

Agent HTTP configuration example:

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

构建本地 Docker 镜像：

```bash
docker build -t mcp-skill-framework:local .
```

将构建好的镜像导出为 tar 文件：

```bash
mkdir -p dist
docker save mcp-skill-framework:local -o dist/mcp-skill-framework-local.tar
```

在另一台机器上导入导出的镜像：

```bash
./scripts/import-docker-image.sh dist/mcp-skill-framework-local.tar
```

运行镜像，并将宿主机 `skills` 文件夹作为默认 skill 来源挂载进去：

```bash
docker run --rm -p 8000:8000 -v "$PWD/skills:/app/skills:ro" mcp-skill-framework:local
```

容器默认启动 streamable HTTP 服务，并从 `/app/skills` 读取插件；该路径通常
应挂载到宿主机的 `skills` 目录。

## 内置 Skills

- `echo.echo`：返回输入文本。
- `local_files.list_directory`：列出本地路径下的文件和目录。

## MCP 工具

已启用的 skill 会直接暴露为 MCP 工具。例如 agent 可以直接调用 `echo.echo`
和 `local_files.list_directory`，不需要先通过 `call_skill` 间接调用。

- `echo.echo`：直接 skill 工具。
- `local_files.list_directory`：直接 skill 工具。
- `list_skills`：兼容辅助工具，用于列出已注册 skill 的名称和描述。
- `describe_skill`：兼容辅助工具，用于返回指定 skill 的元数据和输入 schema。
- `call_skill`：兼容辅助工具，用于通过参数对象调用指定 skill。
- `reload_skills`：在不重启服务的情况下重新加载 `skills.yaml` 和已启用插件。
  新加载的 skill 会同步到 MCP 工具列表。

Agent HTTP 配置示例：

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

## 项目结构

```text
src/mcp_skill_framework/   框架包
skills/                    本地插件包
tests/                     单元测试和 MCP 集成测试
docs/en/                   英文文档
docs/zh/                   中文文档
skills.yaml                默认插件配置
```
