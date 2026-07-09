from pathlib import Path

from mcp_skill_framework.server import create_service


def test_local_files_skill_lists_directory_entries(tmp_path: Path):
    (tmp_path / "alpha.txt").write_text("hello", encoding="utf-8")
    (tmp_path / "nested").mkdir()

    service = create_service("skills.yaml")

    result = service.call_skill(
        "local_files.list_directory",
        {"path": str(tmp_path)},
    )

    assert result == {
        "result": {
            "path": str(tmp_path.resolve()),
            "entries": [
                {
                    "name": "alpha.txt",
                    "path": str((tmp_path / "alpha.txt").resolve()),
                    "type": "file",
                    "size": 5,
                },
                {
                    "name": "nested",
                    "path": str((tmp_path / "nested").resolve()),
                    "type": "directory",
                    "size": None,
                },
            ],
        }
    }
