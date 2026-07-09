from pathlib import Path
from typing import Any

from mcp_skill_framework.config import load_config
from mcp_skill_framework.errors import SkillFrameworkError
from mcp_skill_framework.loader import SkillLoader
from mcp_skill_framework.registry import SkillRegistry


TransportName = str


class SkillMcpService:
    def __init__(self, registry: SkillRegistry, config_path: str | Path | None = None):
        self.registry = registry
        self.config_path = Path(config_path) if config_path is not None else None

    def list_skills(self) -> dict[str, Any]:
        return {"skills": self.registry.list()}

    def describe_skill(self, name: str) -> dict[str, Any]:
        try:
            return {"skill": self.registry.describe(name)}
        except SkillFrameworkError as exc:
            return _error_payload(exc)

    def reload_skills(self) -> dict[str, Any]:
        if self.config_path is None:
            return {
                "error": {
                    "type": "SkillConfigError",
                    "message": "Cannot reload skills without a config path.",
                }
            }
        try:
            registry = SkillRegistry()
            SkillLoader(load_config(self.config_path)).load_into(registry)
            self.registry = registry
            return {"reloaded": True, "skills": self.registry.list()}
        except SkillFrameworkError as exc:
            return _error_payload(exc)

    def call_skill(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        try:
            return {"result": self.registry.call(name, arguments)}
        except SkillFrameworkError as exc:
            return _error_payload(exc)


def create_service(config_path: str | Path) -> SkillMcpService:
    registry = SkillRegistry()
    SkillLoader(load_config(config_path)).load_into(registry)
    return SkillMcpService(registry, config_path)


def create_fastmcp_server(
    config_path: str | Path,
    host: str = "127.0.0.1",
    port: int = 8000,
    path: str = "/mcp",
):
    try:
        from mcp.server.fastmcp import FastMCP
    except ImportError as exc:
        raise RuntimeError(
            "The MCP SDK is not installed. Install it with `pip install -e .[mcp]`."
        ) from exc

    service = create_service(config_path)
    mcp = FastMCP(
        "mcp-skill-framework",
        host=host,
        port=port,
        streamable_http_path=path,
    )

    @mcp.tool()
    def list_skills() -> dict[str, Any]:
        return service.list_skills()

    @mcp.tool()
    def describe_skill(name: str) -> dict[str, Any]:
        return service.describe_skill(name)

    @mcp.tool()
    def call_skill(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        return service.call_skill(name, arguments)

    @mcp.tool()
    def reload_skills() -> dict[str, Any]:
        return service.reload_skills()

    return mcp


def run_stdio_server(config_path: str | Path) -> None:
    create_fastmcp_server(config_path).run(transport="stdio")


def run_streamable_http_server(
    config_path: str | Path,
    host: str = "127.0.0.1",
    port: int = 8000,
    path: str = "/mcp",
) -> None:
    create_fastmcp_server(
        config_path=config_path,
        host=host,
        port=port,
        path=path,
    ).run(transport="streamable-http")


def run_server(
    config_path: str | Path,
    transport: TransportName = "stdio",
    host: str = "127.0.0.1",
    port: int = 8000,
    path: str = "/mcp",
) -> None:
    if transport == "stdio":
        run_stdio_server(config_path)
        return
    if transport == "streamable-http":
        run_streamable_http_server(config_path, host=host, port=port, path=path)
        return
    raise ValueError(f"Unsupported MCP transport: {transport}")


def _error_payload(exc: SkillFrameworkError) -> dict[str, Any]:
    return {
        "error": {
            "type": exc.__class__.__name__,
            "message": str(exc),
        }
    }
