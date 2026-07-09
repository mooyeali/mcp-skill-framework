class SkillFrameworkError(Exception):
    """Base error for the MCP skill framework."""


class SkillAlreadyRegisteredError(SkillFrameworkError):
    def __init__(self, name: str):
        super().__init__(f"Skill already registered: {name}")
        self.name = name


class SkillNotFoundError(SkillFrameworkError):
    def __init__(self, name: str):
        super().__init__(f"Skill not found: {name}")
        self.name = name


class SkillLoadError(SkillFrameworkError):
    def __init__(self, plugin_id: str, message: str):
        super().__init__(f"Failed to load skill plugin {plugin_id}: {message}")
        self.plugin_id = plugin_id


class SkillConfigError(SkillFrameworkError):
    pass
