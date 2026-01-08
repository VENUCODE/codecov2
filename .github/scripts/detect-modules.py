#!/usr/bin/env python3
"""
Detect Python modules in the app/ directory for mutation testing.

Scans the app/ directory for Python modules (.py files), excludes __init__.py
and __pycache__, and outputs a JSON array of module names.
"""

import json
import os
from pathlib import Path


def detect_modules(app_dir="app"):
    """Detect Python modules in the app directory."""
    app_path = Path(app_dir)

    if not app_path.exists():
        raise FileNotFoundError(f"Directory {app_dir} does not exist")

    modules = []

    for py_file in app_path.glob("*.py"):
        # Exclude __init__.py and any __pycache__ files
        if py_file.name == "__init__.py":
            continue

        # Get module name without extension
        module_name = py_file.stem
        modules.append(module_name)

    # Sort for consistent output
    modules.sort()

    return modules


if __name__ == "__main__":
    try:
        modules = detect_modules()
        # Output as JSON array for GitHub Actions
        print(json.dumps(modules))
    except Exception as e:
        print(f"Error detecting modules: {e}", file=os.sys.stderr)
        os.sys.exit(1)
