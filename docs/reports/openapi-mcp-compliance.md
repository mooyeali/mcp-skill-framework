# OpenAPI Compliance Check for External Agent MCP Access

Date: 2026-07-09

## Scope

This report checks whether an external agent connecting to and invoking this MCP
service can be considered compliant with the OpenAPI/Swagger specification at
https://swagger.io/specification/.

## Current Implementation Evidence

The current service exposes MCP tools over stdio:

- Runtime entrypoint: `python -m mcp_skill_framework --config skills.yaml`
- MCP SDK adapter: `src/mcp_skill_framework/server.py`
- Exposed MCP tools:
  - `list_skills`
  - `describe_skill`
  - `call_skill`
  - `reload_skills`
- Integration evidence: `tests/test_mcp_stdio_hotplug.py` starts the service with
  `mcp.client.stdio.stdio_client`, initializes an MCP `ClientSession`, calls
  `call_skill`, calls `reload_skills`, and then calls a newly hot-plugged skill.

No HTTP server, URL paths, OpenAPI document, or Swagger UI artifact currently
exists in the repository.

## OpenAPI Requirements Applied

OpenAPI describes HTTP APIs through an OpenAPI Description document. A compliant
OpenAPI surface needs, at minimum:

- An OpenAPI Description in JSON or YAML.
- A top-level `openapi` version field.
- HTTP API surface modeled through `paths`, `components`, or `webhooks`.
- Operations with request and response schemas.
- HTTP response status codes and media types.
- Optional but normally necessary `servers`, `security`, and reusable schemas.

## Compliance Matrix

| Checkpoint | Current State | Result |
| --- | --- | --- |
| API is an HTTP API surface | Service uses MCP stdio transport, not HTTP | Not compliant / not applicable |
| OpenAPI description file exists | No `openapi.yaml`, `openapi.json`, or Swagger artifact | Not compliant |
| Top-level `openapi` field exists | No OpenAPI document exists | Not compliant |
| URL paths are defined | No HTTP paths exist | Not compliant |
| Request and response schemas are defined in OpenAPI | MCP tool schemas exist in Python, but no OpenAPI schemas exist | Not compliant |
| HTTP status codes and media types are defined | MCP tool responses are structured content, not HTTP responses | Not compliant |
| External agent can connect and call service through MCP | Covered by `tests/test_mcp_stdio_hotplug.py` | MCP-compliant behavior verified |

## Conclusion

The current external-agent connection and invocation path is valid as an MCP
stdio integration, but it is not OpenAPI/Swagger-compliant because OpenAPI is an
HTTP API description standard and this project does not currently expose an HTTP
API or ship an OpenAPI Description document.

This is a protocol boundary issue, not a failure of the MCP implementation. An
external agent using an MCP client should connect through MCP. An external agent
requiring OpenAPI/Swagger needs an HTTP adapter and a matching OpenAPI document.

## Required Work to Become OpenAPI-Compatible

To support external agents that require OpenAPI/Swagger, add an HTTP adapter with
an explicit OpenAPI contract. A minimal compatible surface would be:

- `GET /skills`
  - Maps to `list_skills`.
  - Returns skill names and descriptions.
- `GET /skills/{name}`
  - Maps to `describe_skill`.
  - Returns one skill's metadata and input schema.
- `POST /skills/{name}/call`
  - Maps to `call_skill`.
  - Accepts `{"arguments": {...}}`.
  - Returns `{"result": ...}` or a structured error.
- `POST /skills/reload`
  - Maps to `reload_skills`.
  - Reloads enabled plugins.

The OpenAPI document should define:

- `openapi: 3.1.0`
- `info`
- `servers`
- `paths`
- `components.schemas.SkillSummary`
- `components.schemas.SkillDescription`
- `components.schemas.CallSkillRequest`
- `components.schemas.CallSkillResponse`
- `components.schemas.ErrorResponse`
- explicit `200`, `400`, `404`, and `500` responses

## Recommendation

Keep the existing MCP stdio service as the native MCP integration path. If
OpenAPI compatibility is required for external agents, implement a small HTTP
gateway in front of `SkillMcpService` and validate the generated or maintained
OpenAPI document in tests.
