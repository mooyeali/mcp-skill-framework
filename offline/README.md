# Offline install notes

Target runtime: Python 3.10.12 on Linux x86_64.

1. Copy the entire offline/ directory to the target machine.
2. From inside offline/, install without internet:

```bash
python3.10 -m pip install --no-index --find-links ./wheels "mcp-skill-framework[mcp]==0.1.0"
```

The wheels were downloaded for CPython 3.10 and manylinux2014_x86_64.
