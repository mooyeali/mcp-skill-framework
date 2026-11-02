# 设计文档

## 概览

MCP Skill Framework 是一个 Python 框架，用于通过统一的 MCP 服务暴露可插拔
skill 工具。框架将 skill 发现、注册、调用和传输协议解耦，因此同一组工具可以
同时通过 MCP stdio 和 MCP streamable HTTP 对外服务。

## 目标

- 为 skill 调用提供统一入口。
- 通过本地 Python 包和 `skills.yaml` 支持 skill 增删。
- 通过 `reload_skills` MCP 工具支持热加载。
- 同时支持 MCP stdio 和 MCP streamable HTTP 两种传输协议。
- 保持核心服务无需启动 MCP 进程即可测试。

## 模块职责

| 模块 | 职责 |
| --- | --- |
| `mcp_skill_framework.__main__` | 解析 CLI 参数，并按指定 MCP transport 启动服务。 |
| `mcp_skill_framework.config` | 加载并校验 `skills.yaml`，按配置文件位置解析插件目录。 |
| `mcp_skill_framework.loader` | 导入已启用的插件模块，并调用插件的 `register(registry)` 函数。 |
| `mcp_skill_framework.registry` | 存储 skill 定义，拒绝重复名称，提供列表、描述和调用能力。 |
| `mcp_skill_framework.models` | 定义 `SkillDefinition` 数据模型和 handler 类型。 |
| `mcp_skill_framework.errors` | 定义框架专用异常。 |
| `mcp_skill_framework.server` | 构建与 transport 无关的 `SkillMcpService`，向 FastMCP 注册工具，并运行 stdio 或 streamable HTTP。 |

## 架构

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
         - 来自已启用插件的直接 skill 工具
         - 兼容和管理工具
         - reload_skills
```

`SkillMcpService` 是核心边界。它不关心调用方来自 stdio、streamable HTTP
还是单元测试。协议相关逻辑仅保留在 `create_fastmcp_server`、
`run_stdio_server` 和 `run_streamable_http_server` 中。

## Skill 注册流程

1. CLI 接收配置文件路径。
2. `load_config` 读取 YAML 并生成 `FrameworkConfig`。
3. `SkillLoader` 将插件目录加入 `sys.path`。
4. 已启用插件按 `(order, plugin_id)` 排序。
5. 动态导入每个插件模块。
6. 调用插件的 `register(registry)`，注册一个或多个工具。
7. registry 成为 skill 列表、描述和调用的唯一事实来源。
8. `create_fastmcp_server` 使用 skill 名称和输入 schema，将每个已加载 skill
   直接暴露为 MCP 工具。

## 插件契约

skill 插件是位于配置插件目录下的 Python 包。插件必须暴露
`register(registry)` 函数：

```python
def register(registry):
    registry.register(
        name="example.tool",
        description="Describe what this tool does.",
        input_schema={"type": "object"},
        handler=lambda arguments: {"ok": True},
    )
```

handler 接收 `dict[str, Any]`，返回可 JSON 序列化的数据。

## MCP 工具

框架会将已启用的 skill 直接暴露为 MCP 工具。注册名为 `echo.echo` 的 skill
会在 MCP `list_tools` 中显示为 `echo.echo`，并可按其声明的 input schema
直接调用。

框架同时暴露兼容和管理工具：

| 工具 | 用途 |
| --- | --- |
| `list_skills` | 返回 skill 名称和描述。 |
| `describe_skill` | 返回指定 skill 的名称、描述和输入 schema。 |
| `call_skill` | 兼容辅助工具，用于按名称和参数对象调用 skill。 |
| `reload_skills` | 重新读取 `skills.yaml`，导入已启用插件，并替换当前 registry。 |

## 传输协议

框架支持两种 MCP transport：

- `stdio`：面向本地 agent 的进程级 MCP transport。
- `streamable-http`：HTTP MCP transport，默认路径为 `/mcp`。

两种 transport 使用同一套 FastMCP 工具注册和同一个 `SkillMcpService`，从而保证
不同客户端上的行为一致。

## 热加载

`reload_skills` 会基于当前配置文件重新构建 `SkillRegistry`，并替换运行中
`SkillMcpService` 的 registry。loader 在导入插件前会失效 import cache，并从
`sys.modules` 中移除插件模块，因此运行中的服务可以发现新建或修改过的本地插件包。
reload 成功后，直接 MCP skill 工具会与新的 registry 同步：已移除的 skill
会从工具列表删除，新启用的 skill 会加入工具列表。

## 错误模型

框架异常会转换为结构化 MCP 工具响应：

```json
{
  "error": {
    "type": "SkillNotFoundError",
    "message": "Skill not found: missing.tool"
  }
}
```

当前框架异常包括：

- `SkillFrameworkError`
- `SkillAlreadyRegisteredError`
- `SkillNotFoundError`
- `SkillLoadError`
- `SkillConfigError`

## 内置 Skill

| Skill | 描述 |
| --- | --- |
| `echo.echo` | 返回输入文本。 |
| `local_files.list_directory` | 列出本地路径下的文件和目录。 |

## 测试覆盖

测试覆盖以下内容：

- 配置解析和校验。
- 插件加载、禁用插件和加载错误包装。
- registry 注册、重复名称检测、描述和调用。
- service 层 list、describe、call、reload 行为。
- CLI 默认参数和 HTTP 参数。
- 真实 MCP stdio 客户端集成。
- 真实 MCP streamable HTTP 客户端集成。
