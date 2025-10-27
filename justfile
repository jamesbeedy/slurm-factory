#!/usr/bin/env just --justfile
# Copyright 2025 Vantage Compute Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

uv := require("uv")

project_dir := justfile_directory()
src_dir := project_dir / "slurm_factory"
tests_dir := project_dir / "tests"

export PY_COLORS := "1"
export PYTHONBREAKPOINT := "pdb.set_trace"
export PYTHONPATH := src_dir

uv_run := "uv run --frozen --extra dev"

# Install Docusaurus dependencies
[group("docusaurus")]
docs-install:
    @echo "📦 Installing Docusaurus dependencies..."
    cd docusaurus && yarn install

# Start Docusaurus development server
[group("docusaurus")]
docs-dev: docs-install
    @echo "🚀 Starting Docusaurus development server..."
    cd docusaurus && yarn start

# Start Docusaurus development server on specific port
[group("docusaurus")]
docs-dev-port port="3000": docs-install
    @echo "🚀 Starting Docusaurus development server on port {{port}}..."
    cd docusaurus && yarn start --port {{port}}

# Build Docusaurus for production
[group("docusaurus")]
docs-build: docs-install
    #{{uv_run}} python3 ./scripts/generate_complete_docs.py
    {{uv_run}} python3 ./scripts/update_docs_version.py
    @echo "🏗️ Building Docusaurus for production..."
    cd docusaurus && yarn build

# Serve built Docusaurus site locally
[group("docusaurus")]
docs-serve: docs-build
    @echo "🌐 Serving built Docusaurus site..."
    cd docusaurus && yarn serve

# Clean Docusaurus build artifacts
[group("docusaurus")]
docs-clean:
    @echo "🧹 Cleaning Docusaurus build artifacts..."
    cd docusaurus && rm -rf build .docusaurus

# Show available documentation commands
[group("docusaurus")]
docs-help:
    @echo "📚 Docusaurus Commands:"
    @echo "  docs-install    - Install dependencies"
    @echo "  docs-dev        - Start development server"
    @echo "  docs-dev-port   - Start dev server on specific port"
    @echo "  docs-build      - Build for production"
    @echo "  docs-serve      - Serve built site"
    @echo "  docs-clean      - Clean build artifacts"

[private]
default:
    @just help

# Regenerate uv.lock
[group("dev")]
lock:
    uv lock --no-cache

# Create a development environment
[group("dev")]
env: lock
    uv sync --extra dev

# Upgrade uv.lock with the latest dependencies
[group("dev")]
upgrade:
    uv lock --upgrade

[group("dev")]
build: lock
    uv build --no-cache


# Apply coding style standards to code
[group("lint")]
fmt: lock
    {{uv_run}} ruff format {{src_dir}} --exclude=data
    {{uv_run}} ruff check --fix {{src_dir}} --exclude=data

# Check code against coding style standards
[group("lint")]
lint: lock
    {{uv_run}} codespell {{src_dir}} --skip=data
    {{uv_run}} ruff check {{src_dir}} --exclude=data

# Run static type checker on code
[group("lint")]
typecheck: lock
    {{uv_run}} pyright {{src_dir}}

# Run unit tests only
[group("test")]
unit: lock
    {{uv_run}} pytest {{tests_dir}} -v --tb=short --ignore=data --cov={{src_dir}} --cov-report=term-missing


# Print spack.yaml configuration for CPU-only build (standard)
[group("config")]
show-config-cpu:
    {{uv_run}} python -c "from slurm_factory.spack_yaml import generate_yaml_string; print(generate_yaml_string('25.05', False, False))"

# Print spack.yaml configuration for GPU-enabled build
[group("config")]
show-config-gpu:
    {{uv_run}} python -c "from slurm_factory.spack_yaml import generate_yaml_string; print(generate_yaml_string('25.05', True, False))"

# Print spack.yaml configuration for minimal build (CPU-only, no OpenMPI)
[group("config")]
show-config-minimal:
    {{uv_run}} python -c "from slurm_factory.spack_yaml import generate_yaml_string; print(generate_yaml_string('25.05', False, True))"

# Print spack.yaml configuration for minimal GPU build (with GPU support, no OpenMPI)
[group("config")]
show-config-minimal-gpu:
    {{uv_run}} python -c "from slurm_factory.spack_yaml import generate_yaml_string; print(generate_yaml_string('25.05', True, True))"

# Print spack.yaml configuration with verification enabled (for CI/debugging)
[group("config")]
show-config-verify:
    {{uv_run}} python -c "from slurm_factory.spack_yaml import generate_yaml_string; print(generate_yaml_string('25.05', False, False, True))"

# List all available Slurm versions
[group("config")]
show-versions:
    {{uv_run}} python -c "from slurm_factory.constants import SLURM_VERSIONS; print('Available Slurm versions:'); [print(f'  {k}: {v}') for k, v in SLURM_VERSIONS.items()]"

aws-sync:
    aws s3 cp --profile james-vantage-runtimes /home/bdx/.slurm-factory/slurm-25.05-software.tar.gz s3://vantage-public-assets/slurm/25.05/slurm-latest.tar.gz --acl public-read
