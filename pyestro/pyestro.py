#!/usr/bin/env python3
"""
Entry point script for Pyestro.
"""

import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from pyestro.cli.main import cli

if __name__ == "__main__":
    cli()
