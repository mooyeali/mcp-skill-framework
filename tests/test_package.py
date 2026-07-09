def test_package_exports_version():
    import mcp_skill_framework

    assert isinstance(mcp_skill_framework.__version__, str)
