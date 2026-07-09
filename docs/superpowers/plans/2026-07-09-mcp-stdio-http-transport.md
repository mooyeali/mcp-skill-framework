# MCP Stdio and HTTP Transport Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Serve the same MCP skill tools through both stdio and MCP streamable HTTP.

**Architecture:** Keep `SkillMcpService` as the shared transport-neutral core. Add a FastMCP factory that registers tools once, then dispatch CLI execution to either `stdio` or `streamable-http`.

**Tech Stack:** Python 3.11+, official `mcp` SDK, pytest, anyio.

---

## File Structure

- Modify `src/mcp_skill_framework/server.py`: add FastMCP factory, transport dispatcher, and streamable HTTP runner.
- Modify `src/mcp_skill_framework/__main__.py`: add CLI transport, host, port, and path options.
- Modify `README.md`: document stdio and streamable HTTP startup commands.
- Create `tests/test_cli.py`: verify CLI parser defaults and HTTP options.
- Create `tests/test_mcp_streamable_http.py`: start the HTTP MCP server and connect with the MCP streamable HTTP client.
- Modify `tests/test_mcp_stdio_hotplug.py`: keep stdio path compatible with explicit transport defaults.

### Task 1: CLI Parser

**Files:**
- Modify: `src/mcp_skill_framework/__main__.py`
- Test: `tests/test_cli.py`

- [ ] **Step 1: Write failing parser tests**

```python
from mcp_skill_framework.__main__ import build_parser


def test_parser_defaults_to_stdio_transport():
    args = build_parser().parse_args([])
    assert args.transport == "stdio"
    assert args.config == "skills.yaml"
    assert args.host == "127.0.0.1"
    assert args.port == 8000
    assert args.path == "/mcp"


def test_parser_accepts_streamable_http_options():
    args = build_parser().parse_args([
        "--transport", "streamable-http",
        "--host", "0.0.0.0",
        "--port", "9000",
        "--path", "/custom-mcp",
        "--config", "custom.yaml",
    ])
    assert args.transport == "streamable-http"
    assert args.host == "0.0.0.0"
    assert args.port == 9000
    assert args.path == "/custom-mcp"
    assert args.config == "custom.yaml"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_cli.py -v`
Expected: FAIL because parser has no transport, host, port, or path options.

- [ ] **Step 3: Implement parser options and dispatch**

Update `main()` to call `run_server(args.config, args.transport, args.host, args.port, args.path)`.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_cli.py -v`
Expected: PASS.

### Task 2: Shared FastMCP Factory and HTTP Runner

**Files:**
- Modify: `src/mcp_skill_framework/server.py`
- Test: `tests/test_server.py`

- [ ] **Step 1: Write failing server tests**

Add tests that `create_fastmcp_server("skills.yaml", host="127.0.0.1", port=8765, path="/mcp")` returns a FastMCP object and that `run_server` dispatches unsupported transports with `ValueError`.

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_server.py -v`
Expected: FAIL because `create_fastmcp_server` and `run_server` do not exist.

- [ ] **Step 3: Implement FastMCP factory and runners**

Implement `create_fastmcp_server`, `run_stdio_server`, `run_streamable_http_server`, and `run_server`.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_server.py -v`
Expected: PASS.

### Task 3: Streamable HTTP Integration

**Files:**
- Create: `tests/test_mcp_streamable_http.py`
- Modify: `README.md`

- [ ] **Step 1: Write failing HTTP MCP integration test**

Start `python -m mcp_skill_framework --transport streamable-http --host 127.0.0.1 --port <free_port> --path /mcp --config skills.yaml` as a subprocess, connect to `http://127.0.0.1:<free_port>/mcp` with `mcp.client.streamable_http.streamable_http_client`, initialize `ClientSession`, call `list_skills`, and call `call_skill`.

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_mcp_streamable_http.py -v`
Expected: FAIL because HTTP transport is not wired through the CLI.

- [ ] **Step 3: Implement minimal HTTP support**

Use `FastMCP.run(transport="streamable-http")` and preserve the shared tool registration.

- [ ] **Step 4: Run target tests**

Run:
- `pytest tests/test_cli.py tests/test_server.py tests/test_mcp_stdio_hotplug.py tests/test_mcp_streamable_http.py -v`

Expected: PASS.

### Task 4: Full Verification and Commit

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Document both transports**

Add stdio and streamable HTTP examples.

- [ ] **Step 2: Run full verification**

Run:
- `pytest -v`
- `python -m mcp_skill_framework --help`

Expected: all tests pass; help includes `--transport`, `--host`, `--port`, and `--path`.

- [ ] **Step 3: Commit implementation**

```bash
git add README.md src/mcp_skill_framework/server.py src/mcp_skill_framework/__main__.py tests/test_cli.py tests/test_server.py tests/test_mcp_streamable_http.py docs/superpowers/plans/2026-07-09-mcp-stdio-http-transport.md
git commit -m "feat: support mcp streamable http transport"
```
