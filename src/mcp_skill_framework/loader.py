import importlib
import sys
from pathlib import Path

from mcp_skill_framework.config import FrameworkConfig
from mcp_skill_framework.errors import SkillLoadError
from mcp_skill_framework.registry import SkillRegistry


class SkillLoader:
    def __init__(self, config: FrameworkConfig):
        self.config = config

    def load_into(self, registry: SkillRegistry) -> SkillRegistry:
        plugin_dir = str(Path(self.config.plugin_dir))
        inserted = False
        if plugin_dir not in sys.path:
            sys.path.insert(0, plugin_dir)
            inserted = True

        try:
            for plugin in self.config.enabled_plugins():
                self._load_plugin(plugin.plugin_id, plugin.module, registry)
        finally:
            if inserted:
                try:
                    sys.path.remove(plugin_dir)
                except ValueError:
                    pass

        return registry

    def _load_plugin(self, plugin_id: str, module_name: str, registry: SkillRegistry) -> None:
        try:
            module = importlib.import_module(module_name)
            register = getattr(module, "register")
            register(registry)
        except Exception as exc:
            raise SkillLoadError(plugin_id, str(exc)) from exc
