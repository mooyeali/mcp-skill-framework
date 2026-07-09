from collections.abc import Callable
from dataclasses import dataclass
from typing import Any


SkillHandler = Callable[[dict[str, Any]], Any]


@dataclass(frozen=True)
class SkillDefinition:
    name: str
    description: str
    input_schema: dict[str, Any]
    handler: SkillHandler

    def summary(self) -> dict[str, str]:
        return {
            "name": self.name,
            "description": self.description,
        }

    def describe(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.input_schema,
        }
