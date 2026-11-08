"""Minimal local `.env` loader without adding a dependency."""

import os
from pathlib import Path


def load_local_env(path: Path = Path(".env")) -> None:
    """Load KEY=VALUE pairs from an ignored local file when it exists."""
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", maxsplit=1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))
