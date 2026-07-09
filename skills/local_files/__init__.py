from pathlib import Path


def register(registry):
    registry.register(
        name="local_files.list_directory",
        description="List entries in a local directory.",
        input_schema={
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Directory path to list.",
                },
                "include_hidden": {
                    "type": "boolean",
                    "description": "Whether to include dot-prefixed entries.",
                    "default": False,
                },
            },
            "required": ["path"],
        },
        handler=list_directory,
    )


def list_directory(arguments):
    directory = Path(arguments["path"]).expanduser().resolve()
    include_hidden = bool(arguments.get("include_hidden", False))
    entries = []

    for entry in sorted(directory.iterdir(), key=lambda path: path.name):
        if not include_hidden and entry.name.startswith("."):
            continue
        entries.append(
            {
                "name": entry.name,
                "path": str(entry.resolve()),
                "type": "directory" if entry.is_dir() else "file",
                "size": None if entry.is_dir() else entry.stat().st_size,
            }
        )

    return {
        "path": str(directory),
        "entries": entries,
    }
