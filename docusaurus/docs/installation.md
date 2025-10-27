
# Installation Guide

This guide covers the different ways to install and set up Slurm Factory for building optimized, relocatable Slurm packages using our modern Python CLI.

## Prerequisites

Before installing Slurm Factory, you need to have Docker installed and configured:

```bash
# Install Docker
curl -fsSL https://get.docker.com | sh

# Add your user to the docker group (avoids needing sudo)
sudo usermod -aG docker $USER
newgrp docker

# Verify Docker is working
docker --version
docker run hello-world
```

**System Requirements:**
- **OS**: Ubuntu 20.04+ or equivalent Linux distribution
- **Docker**: 24.0+ (latest stable version recommended)
- **Python**: 3.9+ (automatically handled by pip/pipx)
- **Memory**: 4GB+ RAM recommended for builds (16GB+ optimal)
- **Storage**: 50GB+ free space for build cache and packages

## Installation Methods

### Option 1: Install from PyPI (Recommended)

The easiest way to install Slurm Factory is from PyPI using pip:

```bash
# Install slurm-factory from PyPI
pip install slurm-factory

# Verify installation and check CLI commands
slurm-factory --help

# Test with version info
slurm-factory build --help
```

### Option 2: Install with pipx (Isolated Environment)

For an isolated installation that doesn't interfere with your system Python packages:

```bash
# Install pipx if you don't have it
pip install pipx
pipx ensurepath

# Install slurm-factory with pipx in isolated environment
pipx install slurm-factory

# Verify installation
slurm-factory --help

# Upgrade when needed
pipx upgrade slurm-factory
```

### Option 3: Install from Source (Development)

For development or to get the latest features before release:

```bash
# Install uv (modern Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone the repository
git clone https://github.com/vantagecompute/slurm-factory.git
cd slurm-factory

# Install dependencies and create virtual environment
uv sync

# Run slurm-factory in development mode
uv run slurm-factory --help

# Run tests to verify installation
uv run pytest
```

### Option 4: Development with Justfile

For active development with our task runner:

```bash
# Clone and enter repository
git clone https://github.com/vantagecompute/slurm-factory.git
cd slurm-factory

# Install just task runner
curl --proto '=https' --tlsv1.2 -sSf https://just.systems/install.sh | bash -s -- --to ~/.local/bin

# Install dependencies
just install

# Run tests
just unit

# Build package locally
just build

# See all available tasks
just --list
```

## Verification

After installation, verify that Slurm Factory is working correctly:

```bash
# Check CLI is working
slurm-factory --help

# Check available commands
slurm-factory build --help
slurm-factory clean --help

# Verify Docker integration (should show Docker version)
docker --version

# Test basic functionality (builds a Slurm package)
slurm-factory build --slurm-version 25.05
```

## Configuration

### Environment Variables

Slurm Factory supports these environment variables:

```bash
# Set default project name (used in container naming)
export IF_PROJECT_NAME=my-slurm-builds

# Now all commands use this project by default
slurm-factory build --slurm-version 25.05
```

### Cache Directory

Build caches are stored in your home directory:

```bash
# Default cache location
~/.slurm-factory/
├── builds/           # Built packages (TAR files)
├── spack-buildcache/ # Compiled package binaries
├── spack-sourcecache/# Downloaded source archives
├── binary_index/     # Dependency resolution cache
└── ccache/          # Compiler object cache
```

## Quick Start

Once installed, you can immediately start building Slurm packages:

```bash
# Build latest Slurm with CPU optimizations (default)
slurm-factory build

# Build with GPU support (CUDA/ROCm)
slurm-factory build --gpu

# Build minimal package (smallest size)
slurm-factory build --minimal

# Build specific version
slurm-factory build --slurm-version 24.11

# Use custom project name (for container naming)
slurm-factory --project-name production build --slurm-version 25.05

# Clean up when done
slurm-factory clean --full
```

## Troubleshooting

### Docker Permission Issues
```bash
# Add your user to the docker group
sudo usermod -aG docker $USER

# Log out and back in, or use newgrp
newgrp docker

# Test Docker access
docker ps
```

### Python Path Issues
```bash
# If command not found after pip install
pip install --user slurm-factory
export PATH=$PATH:~/.local/bin

# Or use python -m for direct module execution
python -m slurm_factory --help
```

### Storage Issues
```bash
# Check available space (needs 50GB+)
df -h ~/.slurm-factory/

# Clean cache if needed
slurm-factory clean --full

# Or manually clean cache directory
rm -rf ~/.slurm-factory/spack-buildcache/
```

## Next Steps

- See the [Architecture Overview](/slurm-factory/architecture/) to understand how Slurm Factory works
- Check out [Examples](/slurm-factory/examples/) for common usage patterns and advanced scenarios
- Review [API Reference](/slurm-factory/api-reference/) for complete CLI and Python API documentation
- Read [Deployment Guide](/slurm-factory/deployment/) for installing and configuring built packages
