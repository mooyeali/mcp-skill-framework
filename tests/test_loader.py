from pathlib import Path

import pytest

from mcp_skill_framework.config import load_config
from mcp_skill_framework.errors import SkillLoadError, SkillNotFoundError
from mcp_skill_framework.loader import SkillLoader
from mcp_skill_framework.registry import SkillRegistry


def write_plugin(root: Path, name: str, body: str):
    plugin_dir = root / name
    plugin_dir.mkdir(parents=True)
    (plugin_dir / "__init__.py").write_text(body, encoding="utf-8")


def test_loader_registers_enabled_plugins(tmp_path: Path):
    skill_root = tmp_path / "skills"
    write_plugin(
        skill_root,
        "echo",
        """
def register(registry):
    registry.register(
        name="echo.echo",
        description="Echo text.",
        input_schema={"type": "object"},
        handler=lambda arguments: {"text": arguments["text"]},
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
    registry = SkillRegistry()

    SkillLoader(load_config(config_file)).load_into(registry)

    assert registry.call("echo.echo", {"text": "loaded"}) == {"text": "loaded"}


def test_loader_skips_disabled_plugins(tmp_path: Path):
    skill_root = tmp_path / "skills"
    write_plugin(
        skill_root,
        "echo",
        """
def register(registry):
    registry.register("echo.echo", "Echo text.", {}, lambda arguments: arguments)
""",
    )
    config_file = tmp_path / "skills.yaml"
    config_file.write_text(
        """
plugin_dir: skills
plugins:
  echo:
    enabled: false
""",
        encoding="utf-8",
    )
    registry = SkillRegistry()

    SkillLoader(load_config(config_file)).load_into(registry)

    with pytest.raises(SkillNotFoundError):
        registry.call("echo.echo", {})


def test_loader_wraps_registration_errors(tmp_path: Path):
    skill_root = tmp_path / "skills"
    write_plugin(
        skill_root,
        "broken",
        """
def register(registry):
    raise RuntimeError("boom")
""",
    )
    config_file = tmp_path / "skills.yaml"
    config_file.write_text(
        """
plugin_dir: skills
plugins:
  broken:
    enabled: true
""",
        encoding="utf-8",
    )

    with pytest.raises(SkillLoadError, match="broken"):
        SkillLoader(load_config(config_file)).load_into(SkillRegistry())
