from mcp_skill_framework.registry import SkillRegistry
from mcp_skill_framework.server import SkillMcpService, create_service


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
