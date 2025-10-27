#!/bin/bash

# Extract version from pyproject.toml and set as environment variable
VERSION=$(grep '^version = ' ../pyproject.toml | sed 's/version = "\(.*\)"/\1/')
export DOCUSAURUS_PROJECT_VERSION="$VERSION"

echo "Building Docusaurus with version: $VERSION"
yarn build