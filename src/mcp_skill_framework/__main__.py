import argparse

from mcp_skill_framework.server import run_stdio_server


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m mcp_skill_framework",
        description="Run the MCP skill framework stdio server.",
    )
    parser.add_argument(
        "--config",
        default="skills.yaml",
        help="Path to the skill plugin configuration file.",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    run_stdio_server(args.config)


if __name__ == "__main__":
    main()
