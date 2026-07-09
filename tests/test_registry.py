import pytest

from mcp_skill_framework.errors import (
    SkillAlreadyRegisteredError,
    SkillNotFoundError,
)
from mcp_skill_framework.registry import SkillRegistry


def test_register_list_describe_and_call_skill():
    registry = SkillRegistry()

    registry.register(
        name="echo.echo",
        description="Return text.",
        input_schema={
            "type": "object",
            "properties": {"text": {"type": "string"}},
            "required": ["text"],
        },
        handler=lambda arguments: {"text": arguments["text"]},
    )

    assert registry.list() == [
        {
            "name": "echo.echo",
            "description": "Return text.",
        }
    ]
    assert registry.describe("echo.echo") == {
        "name": "echo.echo",
        "description": "Return text.",
        "input_schema": {
            "type": "object",
            "properties": {"text": {"type": "string"}},
            "required": ["text"],
        },
    }
    assert registry.call("echo.echo", {"text": "hello"}) == {"text": "hello"}


def test_rejects_duplicate_skill_names():
    registry = SkillRegistry()
    registry.register("demo.tool", "Demo.", {}, lambda arguments: arguments)

    with pytest.raises(SkillAlreadyRegisteredError):
        registry.register("demo.tool", "Demo.", {}, lambda arguments: arguments)


def test_missing_skill_raises_clear_error():
    registry = SkillRegistry()

    with pytest.raises(SkillNotFoundError):
        registry.describe("missing.tool")

    with pytest.raises(SkillNotFoundError):
        registry.call("missing.tool", {})
