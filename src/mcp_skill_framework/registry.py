from collections.abc import Mapping
from typing import Any

from mcp_skill_framework.errors import (
    SkillAlreadyRegisteredError,
    SkillNotFoundError,
)
from mcp_skill_framework.models import SkillDefinition, SkillHandler


class SkillRegistry:
    def __init__(self):
        self._skills: dict[str, SkillDefinition] = {}

    def register(
        self,
        name: str,
        description: str,
        input_schema: Mapping[str, Any],
        handler: SkillHandler,
    ) -> None:
        if name in self._skills:
            raise SkillAlreadyRegisteredError(name)
        self._skills[name] = SkillDefinition(
            name=name,
            description=description,
            input_schema=dict(input_schema),
            handler=handler,
        )

    def list(self) -> list[dict[str, str]]:
        return [skill.summary() for skill in self._skills.values()]

    def describe(self, name: str) -> dict[str, Any]:
        return self._get(name).describe()

    def call(self, name: str, arguments: Mapping[str, Any]) -> Any:
        return self._get(name).handler(dict(arguments))

    def _get(self, name: str) -> SkillDefinition:
        try:
            return self._skills[name]
        except KeyError as exc:
            raise SkillNotFoundError(name) from exc
