from collections.abc import Callable
from pathlib import Path
from keyword import iskeyword
from typing import Any

from mcp_skill_framework.config import load_config
from mcp_skill_framework.errors import SkillFrameworkError
from mcp_skill_framework.loader import SkillLoader
from mcp_skill_framework.models import SkillDefinition
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
        result = service.reload_skills()
        if result.get("reloaded") is True:
            sync_direct_skill_tools()
        return result

    direct_tool_names: set[str] = set()

    def sync_direct_skill_tools() -> None:
        current_skill_names = {skill.name for skill in service.registry.definitions()}
        for tool_name in sorted(direct_tool_names - current_skill_names):
            mcp.remove_tool(tool_name)
            direct_tool_names.remove(tool_name)
        for skill in service.registry.definitions():
            if skill.name not in direct_tool_names:
                _add_direct_skill_tool(mcp, service, skill)
                direct_tool_names.add(skill.name)

    sync_direct_skill_tools()

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


def _add_direct_skill_tool(mcp: Any, service: SkillMcpService, skill: SkillDefinition) -> None:
    direct_skill_tool = _build_direct_skill_tool(service, skill)
    mcp.add_tool(
        direct_skill_tool,
        name=skill.name,
        description=skill.description,
        structured_output=True,
    )


def _build_direct_skill_tool(
    service: SkillMcpService,
    skill: SkillDefinition,
) -> Callable[..., dict[str, Any]]:
    parameter_specs = _parameter_specs_from_input_schema(skill.input_schema)
    function_name = _python_function_name(skill.name)
    namespace: dict[str, Any] = {
        "Any": Any,
        "_invoke_direct_skill": _invoke_direct_skill,
        "_service": service,
        "_skill_name": skill.name,
    }
    signature_parts = []
    argument_parts = []
    for index, (name, schema, required) in enumerate(parameter_specs):
        annotation_name = f"_annotation_{index}"
        namespace[annotation_name] = _annotation_from_schema(schema)
        part = f"{name}: {annotation_name}"
        if not required:
            default_name = f"_default_{index}"
            namespace[default_name] = schema.get("default", None)
            part += f" = {default_name}"
        signature_parts.append(part)
        argument_parts.append(f"{name!r}: {name}")

    if signature_parts:
        signature = "*, " + ", ".join(signature_parts)
    else:
        signature = ""
    arguments = "{" + ", ".join(argument_parts) + "}"
    source = (
        f"def {function_name}({signature}) -> dict[str, Any]:\n"
        f"    return _invoke_direct_skill(_service, _skill_name, {arguments})\n"
    )
    exec(source, namespace)
    return namespace[function_name]


def _invoke_direct_skill(
    service: SkillMcpService,
    skill_name: str,
    arguments: dict[str, Any],
) -> dict[str, Any]:
    try:
        return {"result": service.registry.call(skill_name, arguments)}
    except SkillFrameworkError as exc:
        return _error_payload(exc)


def _parameter_specs_from_input_schema(
    input_schema: dict[str, Any],
) -> list[tuple[str, dict[str, Any], bool]]:
    properties = input_schema.get("properties", {})
    required = set(input_schema.get("required", []))
    if not isinstance(properties, dict):
        properties = {}
    parameters = []
    for name, schema in properties.items():
        if not isinstance(name, str) or not name.isidentifier() or iskeyword(name):
            continue
        if not isinstance(schema, dict):
            schema = {}
        parameters.append((name, schema, name in required))
    return parameters


def _annotation_from_schema(schema: dict[str, Any]) -> Any:
    schema_type = schema.get("type")
    if schema_type == "string":
        return str
    if schema_type == "integer":
        return int
    if schema_type == "number":
        return float
    if schema_type == "boolean":
        return bool
    if schema_type == "array":
        return list[Any]
    if schema_type == "object":
        return dict[str, Any]
    return Any


def _python_function_name(skill_name: str) -> str:
    return "skill_" + "".join(char if char.isalnum() else "_" for char in skill_name)
