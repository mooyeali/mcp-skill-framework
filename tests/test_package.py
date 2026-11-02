def test_package_exports_version():
    import mcp_skill_framework

    assert isinstance(mcp_skill_framework.__version__, str)


def test_package_supports_python_310_target_runtime():
    import tomllib

    with open("pyproject.toml", "rb") as pyproject:
        metadata = tomllib.load(pyproject)

    assert metadata["project"]["requires-python"] == ">=3.10"
