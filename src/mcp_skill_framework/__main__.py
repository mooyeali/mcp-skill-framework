import argparse

from mcp_skill_framework.server import run_server


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m mcp_skill_framework",
        description="Run the MCP skill framework server.",
    )
    parser.add_argument(
        "--config",
        default="skills.yaml",
        help="Path to the skill plugin configuration file.",
    )
    parser.add_argument(
        "--transport",
        choices=["stdio", "streamable-http"],
        default="stdio",
        help="MCP transport to serve.",
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host for streamable-http transport.",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port for streamable-http transport.",
    )
    parser.add_argument(
        "--path",
        default="/mcp",
        help="HTTP path for streamable-http transport.",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    run_server(
        config_path=args.config,
        transport=args.transport,
        host=args.host,
        port=args.port,
        path=args.path,
    )


if __name__ == "__main__":
    main()
