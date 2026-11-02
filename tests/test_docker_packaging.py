from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_dockerfile_runs_http_server_with_host_skills_mount_point():
    dockerfile = (ROOT / "Dockerfile").read_text(encoding="utf-8")

    assert "pip install --no-cache-dir .[mcp]" in dockerfile
    assert "COPY docker/skills.yaml /app/skills.yaml" in dockerfile
    assert '"/app/skills"' in dockerfile
    assert '"--transport", "streamable-http"' in dockerfile
    assert '"--host", "0.0.0.0"' in dockerfile
    assert '"--config", "/app/skills.yaml"' in dockerfile


def test_container_default_config_reads_skills_from_app_mount():
    config = (ROOT / "docker" / "skills.yaml").read_text(encoding="utf-8")

    assert "plugin_dir: /app/skills" in config
    assert "echo:" in config
    assert "local_files:" in config


def test_readme_documents_docker_build_and_host_skills_mount():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    assert "docker build -t mcp-skill-framework:local ." in readme
    assert "-v \"$PWD/skills:/app/skills:ro\"" in readme
    assert "http://127.0.0.1:8000/mcp" in readme


def test_import_script_loads_exported_docker_image_tar():
    script = (ROOT / "scripts" / "import-docker-image.sh").read_text(encoding="utf-8")

    assert 'DEFAULT_IMAGE_TAR="${REPO_ROOT}/dist/mcp-skill-framework-local.tar"' in script
    assert 'IMAGE_TAR="${1:-${DEFAULT_IMAGE_TAR}}"' in script
    assert 'docker load -i "${IMAGE_TAR}"' in script
    assert "docker image inspect mcp-skill-framework:local" in script


def test_readme_documents_docker_image_export_and_import():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    assert "mkdir -p dist" in readme
    assert "docker save mcp-skill-framework:local -o dist/mcp-skill-framework-local.tar" in readme
    assert "./scripts/import-docker-image.sh dist/mcp-skill-framework-local.tar" in readme
