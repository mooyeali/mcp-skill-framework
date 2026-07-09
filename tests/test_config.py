from pathlib import Path

import pytest

from mcp_skill_framework.config import load_config
from mcp_skill_framework.errors import SkillConfigError


def test_load_config_defaults_module_and_sorts_plugins(tmp_path: Path):
    config_file = tmp_path / "skills.yaml"
    config_file.write_text(
        """
plugin_dir: local_skills
plugins:
  second:
    enabled: true
    order: 20
  first:
    enabled: true
    module: custom_first
    order: 10
""",
        encoding="utf-8",
    )

    config = load_config(config_file)

    assert config.plugin_dir == tmp_path / "local_skills"
    assert [plugin.plugin_id for plugin in config.enabled_plugins()] == [
        "first",
        "second",
    ]
    assert config.plugins["second"].module == "second"
    assert config.plugins["first"].module == "custom_first"


def test_disabled_plugins_are_not_enabled(tmp_path: Path):
    config_file = tmp_path / "skills.yaml"
    config_file.write_text(
        """
plugins:
  echo:
    enabled: false
  enabled:
    enabled: true
""",
        encoding="utf-8",
    )

    config = load_config(config_file)

    assert [plugin.plugin_id for plugin in config.enabled_plugins()] == ["enabled"]


def test_invalid_config_root_raises(tmp_path: Path):
    config_file = tmp_path / "skills.yaml"
    config_file.write_text("- not-a-map\n", encoding="utf-8")

    with pytest.raises(SkillConfigError):
        load_config(config_file)
