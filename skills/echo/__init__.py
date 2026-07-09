def register(registry):
    registry.register(
        name="echo.echo",
        description="Return the provided text.",
        input_schema={
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "Text to echo.",
                }
            },
            "required": ["text"],
        },
        handler=echo,
    )


def echo(arguments):
    return {"text": arguments["text"]}
