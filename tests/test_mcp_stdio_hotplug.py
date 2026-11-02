import sys
from pathlib import Path

import pytest
from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.anyio
async def test_mcp_stdio_server_hot_plugs_skill_after_startup(tmp_path: Path):
    plugin_root = tmp_path / "skills"
    plugin_root.mkdir()
    _write_plugin(
        plugin_root,
        "echo",
        """
def register(registry):
    registry.register(
        "echo.echo",
        "Echo text.",
        {
            "type": "object",
            "properties": {"text": {"type": "string"}},
            "required": ["text"],
        },
        lambda arguments: arguments,
    )
""",
    )
    config_file = tmp_path / "skills.yaml"
    config_file.write_text(
        """
plugin_dir: skills
plugins:
  echo:
    enabled: true
""",
        encoding="utf-8",
    )
    params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "mcp_skill_framework", "--config", str(config_file)],
        cwd=Path(__file__).resolve().parents[1],
    )

    async with stdio_client(params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            tools = await session.list_tools()
            assert "echo.echo" in {tool.name for tool in tools.tools}

            echoed = await session.call_tool("echo.echo", {"text": "stdio"})
            assert echoed.structuredContent == {"result": {"text": "stdio"}}

            missing = await session.call_tool(
                "call_skill",
                {"name": "hotplug.ping", "arguments": {}},
            )
            assert missing.structuredContent == {
                "error": {
                    "type": "SkillNotFoundError",
                    "message": "Skill not found: hotplug.ping",
                }
            }

            _write_plugin(
                plugin_root,
                "hotplug",
                """
def register(registry):
    registry.register(
        "hotplug.ping",
        "Return a hot-plug response.",
        {},
        lambda arguments: {"pong": True},
    )
""",
            )
            config_file.write_text(
                """
plugin_dir: skills
plugins:
  echo:
    enabled: true
  hotplug:
    enabled: true
""",
                encoding="utf-8",
            )

            reloaded = await session.call_tool("reload_skills", {})
            assert reloaded.structuredContent == {
                "reloaded": True,
                "skills": [
                    {"name": "echo.echo", "description": "Echo text."},
                    {
                        "name": "hotplug.ping",
                        "description": "Return a hot-plug response.",
                    },
                ],
            }

            tools = await session.list_tools()
            assert "hotplug.ping" in {tool.name for tool in tools.tools}

            plugged = await session.call_tool("hotplug.ping", {})
            assert plugged.structuredContent == {"result": {"pong": True}}


def _write_plugin(root: Path, name: str, body: str) -> None:
    plugin_dir = root / name
    plugin_dir.mkdir()
    (plugin_dir / "__init__.py").write_text(body, encoding="utf-8")
