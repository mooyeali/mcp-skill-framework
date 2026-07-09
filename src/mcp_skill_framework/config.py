from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from mcp_skill_framework.errors import SkillConfigError


@dataclass(frozen=True)
class PluginConfig:
    plugin_id: str
    module: str
    enabled: bool = True
    order: int = 100


@dataclass(frozen=True)
class FrameworkConfig:
    config_path: Path
    plugin_dir: Path
    plugins: dict[str, PluginConfig]

    def enabled_plugins(self) -> list[PluginConfig]:
        return sorted(
            (plugin for plugin in self.plugins.values() if plugin.enabled),
            key=lambda plugin: (plugin.order, plugin.plugin_id),
        )


def load_config(path: str | Path) -> FrameworkConfig:
    config_path = Path(path).expanduser().resolve()
    try:
        raw = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    except OSError as exc:
        raise SkillConfigError(f"Cannot read config {config_path}: {exc}") from exc
    except yaml.YAMLError as exc:
        raise SkillConfigError(f"Invalid YAML in {config_path}: {exc}") from exc

    if not isinstance(raw, dict):
        raise SkillConfigError("Config root must be a mapping")

    plugin_dir_value = raw.get("plugin_dir", "skills")
    if not isinstance(plugin_dir_value, str):
        raise SkillConfigError("plugin_dir must be a string")
    plugin_dir = (config_path.parent / plugin_dir_value).resolve()

    plugins_raw = raw.get("plugins", {})
    if not isinstance(plugins_raw, dict):
        raise SkillConfigError("plugins must be a mapping")

    plugins: dict[str, PluginConfig] = {}
    for plugin_id, plugin_raw in plugins_raw.items():
        if not isinstance(plugin_id, str):
            raise SkillConfigError("plugin ids must be strings")
        if plugin_raw is None:
            plugin_raw = {}
        if not isinstance(plugin_raw, dict):
            raise SkillConfigError(f"Plugin {plugin_id} config must be a mapping")
        plugins[plugin_id] = _parse_plugin(plugin_id, plugin_raw)

    return FrameworkConfig(
        config_path=config_path,
        plugin_dir=plugin_dir,
        plugins=plugins,
    )


def _parse_plugin(plugin_id: str, raw: dict[str, Any]) -> PluginConfig:
    module = raw.get("module", plugin_id)
    enabled = raw.get("enabled", True)
    order = raw.get("order", 100)

    if not isinstance(module, str):
        raise SkillConfigError(f"Plugin {plugin_id} module must be a string")
    if not isinstance(enabled, bool):
        raise SkillConfigError(f"Plugin {plugin_id} enabled must be a boolean")
    if not isinstance(order, int):
        raise SkillConfigError(f"Plugin {plugin_id} order must be an integer")

    return PluginConfig(
        plugin_id=plugin_id,
        module=module,
        enabled=enabled,
        order=order,
    )
