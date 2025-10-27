#!/usr/bin/env python3
"""Update Docusaurus version data from pyproject.toml"""

import re
import tomllib
from datetime import datetime
from pathlib import Path


def get_project_version() -> str:
    """Extract version from pyproject.toml"""
    pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
    
    with open(pyproject_path, "rb") as f:
        pyproject = tomllib.load(f)
    
    return pyproject["project"]["version"]


def update_version_yml(version: str) -> None:
    """Update the version.yml file in docusaurus/data/"""
    version_file = Path(__file__).parent.parent / "docusaurus" / "data" / "version.yml"
    
    # Read current content
    content = version_file.read_text()
    
    # Update version line
    content = re.sub(
        r'^version: ".*"$',
        f'version: "{version}"',
        content,
        flags=re.MULTILINE
    )
    
    # Update lastUpdated to today's date
    today = datetime.now().strftime("%Y-%m-%d")
    content = re.sub(
        r'^lastUpdated: ".*"$',
        f'lastUpdated: "{today}"',
        content,
        flags=re.MULTILINE
    )
    
    # Write updated content
    version_file.write_text(content)
    print(f"✓ Updated version to {version} in {version_file}")


def main():
    version = get_project_version()
    update_version_yml(version)
    print(f"✓ Docusaurus version data updated to {version}")


if __name__ == "__main__":
    main()
