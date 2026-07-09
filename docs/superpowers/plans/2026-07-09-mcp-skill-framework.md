# MCP Skill Framework Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Python MCP service framework that is the unified entry point for skill calls and supports pluggable skill modules.

**Architecture:** The framework uses a thin MCP adapter over a testable core. `SkillRegistry` owns skill metadata and invocation, `SkillLoader` imports enabled plugins from `skills.yaml`, and plugins register tools through a stable `register(registry)` function.

**Tech Stack:** Python 3.11+, pytest, PyYAML, optional official `mcp` Python package.

---

## File Structure

- Create `pyproject.toml`: package metadata, dependencies, pytest config, console script.
- Create `README.md`: quickstart and plugin contract.
- Create `skills.yaml`: default plugin configuration.
- Create `src/mcp_skill_framework/models.py`: immutable skill metadata model.
- Create `src/mcp_skill_framework/errors.py`: framework exception types.
- Create `src/mcp_skill_framework/registry.py`: registration, description, listing, invocation.
- Create `src/mcp_skill_framework/config.py`: YAML config loading and validation.
- Create `src/mcp_skill_framework/loader.py`: plugin import and registration.
- Create `src/mcp_skill_framework/server.py`: MCP-facing entry points and optional SDK bridge.
- Create `src/mcp_skill_framework/__main__.py`: CLI entry point.
- Create `skills/echo/__init__.py`: sample plugin.
- Create `tests/`: focused unit tests for registry, config, loader, and server adapter.

### Task 1: Package Skeleton

**Files:**
- Create: `pyproject.toml`
- Create: `README.md`
- Create: `src/mcp_skill_framework/__init__.py`
- Test: `tests/test_package.py`

- [ ] **Step 1: Write the failing package import test**

```python
def test_package_exports_version():
    import mcp_skill_framework

    assert isinstance(mcp_skill_framework.__version__, str)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_package.py -v`
Expected: FAIL because `mcp_skill_framework` does not exist.

- [ ] **Step 3: Add package metadata and version export**

Create `pyproject.toml` with project metadata, pytest path config, `pyyaml`, and optional `mcp`.

Create `src/mcp_skill_framework/__init__.py`:

```python
__version__ = "0.1.0"
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_package.py -v`
Expected: PASS.

### Task 2: Skill Registry

**Files:**
- Create: `src/mcp_skill_framework/errors.py`
- Create: `src/mcp_skill_framework/models.py`
- Create: `src/mcp_skill_framework/registry.py`
- Test: `tests/test_registry.py`

- [ ] **Step 1: Write failing tests for registration and invocation**

Tests must cover listing, describing, invoking, duplicate rejection, and missing skill errors.

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_registry.py -v`
Expected: FAIL because registry modules do not exist.

- [ ] **Step 3: Implement registry models and errors**

Add `SkillDefinition` dataclass with `name`, `description`, `input_schema`, and `handler`.

Add explicit errors: `SkillFrameworkError`, `SkillAlreadyRegisteredError`, `SkillNotFoundError`.

- [ ] **Step 4: Implement `SkillRegistry`**

Implement `register`, `list`, `describe`, and `call`.

- [ ] **Step 5: Run test to verify it passes**

Run: `pytest tests/test_registry.py -v`
Expected: PASS.

### Task 3: Config Loader

**Files:**
- Create: `src/mcp_skill_framework/config.py`
- Test: `tests/test_config.py`

- [ ] **Step 1: Write failing config tests**

Tests must cover default module names, disabled plugins, deterministic ordering, and invalid root structure.

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_config.py -v`
Expected: FAIL because `load_config` does not exist.

- [ ] **Step 3: Implement YAML config parsing**

Implement `PluginConfig`, `FrameworkConfig`, and `load_config(path)`.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_config.py -v`
Expected: PASS.

### Task 4: Plugin Loader and Echo Skill

**Files:**
- Create: `src/mcp_skill_framework/loader.py`
- Create: `skills.yaml`
- Create: `skills/echo/__init__.py`
- Test: `tests/test_loader.py`

- [ ] **Step 1: Write failing loader tests**

Tests must cover loading enabled plugins, skipping disabled plugins, and wrapping registration failures as `SkillLoadError`.

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_loader.py -v`
Expected: FAIL because `SkillLoader` does not exist.

- [ ] **Step 3: Implement plugin loading**

Add `SkillLoadError`. Implement plugin directory insertion into `sys.path`, dynamic import, `register(registry)` lookup, and cleanup.

- [ ] **Step 4: Add sample echo plugin**

Create `skills/echo/__init__.py` that registers `echo.echo`.

- [ ] **Step 5: Run test to verify it passes**

Run: `pytest tests/test_loader.py -v`
Expected: PASS.

### Task 5: MCP Server Adapter

**Files:**
- Create: `src/mcp_skill_framework/server.py`
- Create: `src/mcp_skill_framework/__main__.py`
- Test: `tests/test_server.py`

- [ ] **Step 1: Write failing server adapter tests**

Tests must call `list_skills`, `describe_skill`, and `call_skill` directly without starting a subprocess.

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_server.py -v`
Expected: FAIL because server adapter does not exist.

- [ ] **Step 3: Implement server adapter functions**

Create a `SkillMcpService` class that wraps a registry and exposes structured methods for list, describe, and call.

- [ ] **Step 4: Implement optional MCP SDK bridge**

Implement `run_stdio_server(config_path)` using the official `mcp.server.fastmcp.FastMCP` package when installed. If the optional package is missing, raise a clear runtime error that tells the user to install `.[mcp]`.

- [ ] **Step 5: Add CLI entry point**

Implement `python -m mcp_skill_framework --config skills.yaml`.

- [ ] **Step 6: Run test to verify it passes**

Run: `pytest tests/test_server.py -v`
Expected: PASS.

### Task 6: Full Verification

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Document usage**

Document installation, `pytest`, `python -m mcp_skill_framework --config skills.yaml`, and plugin creation.

- [ ] **Step 2: Run full test suite**

Run: `pytest -v`
Expected: all tests PASS.

- [ ] **Step 3: Run import smoke check**

Run: `python -m mcp_skill_framework --help`
Expected: help text includes `--config`.

- [ ] **Step 4: Commit implementation**

```bash
git add .
git commit -m "feat: add python mcp skill framework"
```
