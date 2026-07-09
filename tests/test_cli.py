from mcp_skill_framework.__main__ import build_parser


def test_parser_defaults_to_stdio_transport():
    args = build_parser().parse_args([])

    assert args.transport == "stdio"
    assert args.config == "skills.yaml"
    assert args.host == "127.0.0.1"
    assert args.port == 8000
    assert args.path == "/mcp"


def test_parser_accepts_streamable_http_options():
    args = build_parser().parse_args(
        [
            "--transport",
            "streamable-http",
            "--host",
            "0.0.0.0",
            "--port",
            "9000",
            "--path",
            "/custom-mcp",
            "--config",
            "custom.yaml",
        ]
    )

    assert args.transport == "streamable-http"
    assert args.host == "0.0.0.0"
    assert args.port == 9000
    assert args.path == "/custom-mcp"
    assert args.config == "custom.yaml"
