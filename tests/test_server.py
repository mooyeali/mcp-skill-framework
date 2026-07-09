from pathlib import Path

import pytest

from mcp_skill_framework.registry import SkillRegistry
from mcp_skill_framework.server import (
    SkillMcpService,
    create_fastmcp_server,
    create_service,
    run_server,
)


def test_service_exposes_list_describe_and_call():
    registry = SkillRegistry()
    registry.register(
        name="echo.echo",
        description="Echo text.",
        input_schema={"type": "object"},
        handler=lambda arguments: {"text": arguments["text"]},
    )
    service = SkillMcpService(registry)

    assert service.list_skills() == {
        "skills": [{"name": "echo.echo", "description": "Echo text."}]
    }
    assert service.describe_skill("echo.echo") == {
        "skill": {
            "name": "echo.echo",
            "description": "Echo text.",
            "input_schema": {"type": "object"},
        }
    }
    assert service.call_skill("echo.echo", {"text": "hi"}) == {
        "result": {"text": "hi"}
    }


def test_service_returns_structured_error_for_missing_skill():
    service = SkillMcpService(SkillRegistry())

    assert service.call_skill("missing.tool", {}) == {
        "error": {
            "type": "SkillNotFoundError",
            "message": "Skill not found: missing.tool",
        }
    }


def test_create_service_loads_configured_plugins():
    service = create_service("skills.yaml")

    assert service.call_skill("echo.echo", {"text": "configured"}) == {
        "result": {"text": "configured"}
    }


def test_service_can_reload_plugins_after_startup(tmp_path: Path):
    plugin_root = tmp_path / "skills"
    plugin_root.mkdir()
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
    echo_dir = plugin_root / "echo"
    echo_dir.mkdir()
    (echo_dir / "__init__.py").write_text(
        """
def register(registry):
    registry.register("echo.echo", "Echo text.", {}, lambda arguments: arguments)
""",
        encoding="utf-8",
    )
    service = create_service(config_file)

    assert service.call_skill("hotplug.ping", {})["error"]["type"] == "SkillNotFoundError"

    hotplug_dir = plugin_root / "hotplug"
    hotplug_dir.mkdir()
    (hotplug_dir / "__init__.py").write_text(
        """
def register(registry):
    registry.register(
        "hotplug.ping",
        "Return a hot-plug response.",
        {},
        lambda arguments: {"pong": True},
    )
""",
        encoding="utf-8",
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

    assert service.reload_skills() == {
        "reloaded": True,
        "skills": [
            {"name": "echo.echo", "description": "Echo text."},
            {"name": "hotplug.ping", "description": "Return a hot-plug response."},
        ],
    }
    assert service.call_skill("hotplug.ping", {}) == {"result": {"pong": True}}


def test_create_fastmcp_server_registers_shared_tools():
    mcp = create_fastmcp_server(
        "skills.yaml",
        host="127.0.0.1",
        port=8765,
        path="/mcp",
    )

    assert mcp.name == "mcp-skill-framework"


def test_run_server_rejects_unsupported_transport():
    with pytest.raises(ValueError, match="Unsupported MCP transport"):
        run_server(
            config_path="skills.yaml",
            transport="websocket",
            host="127.0.0.1",
            port=8000,
            path="/mcp",
        )
