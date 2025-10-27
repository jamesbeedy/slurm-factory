------

title: "Slurm Factory - Modern HPC Cluster Builder"title: "Vantage CLI - Overview"

description: "Build optimized Slurm packages using Docker containers and Spack package manager"description: "Authenticate, manage profiles & clusters, deploy apps, and run GraphQL queries against Vantage Compute"

slug: /slug: /

------



# Slurm Factory Documentation## The unified command-line interface for Vantage Compute



<div style={{display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem', flexWrap: 'wrap'}}>Vantage CLI is a modern async Python tool that unifies authentication, profile management, cluster operations and GraphQL querying against the Vantage Compute platform.

  <img src="https://img.shields.io/badge/license-Apache--2.0-blue.svg" alt="License" />

  <img src="https://img.shields.io/badge/python-3.11+-blue.svg" alt="Python" />

  <img src="https://img.shields.io/badge/slurm-25.05-green.svg" alt="Slurm" />### Quick Start

  <img src="https://img.shields.io/badge/platform-linux-lightgrey.svg" alt="Platform" />

</div>Install from pypi:



<div style={{display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '0.5rem', marginBottom: '2rem', flexWrap: 'wrap'}}>```bash

  <img src="https://img.shields.io/github/contributors/vantagecompute/slurm-factory?logo=github&style=plastic" alt="Github Contributors" />uv venv

  <img src="https://img.shields.io/github/issues-pr/vantagecompute/slurm-factory?label=pull-requests&logo=github&style=plastic" alt="Github Pull Requests" />source .venv/bin/activate

  <img src="https://img.shields.io/github/issues/vantagecompute/slurm-factory?label=issues&logo=github&style=plastic" alt="Github Issues" />

</div>uv pip install vantage-cli

```

Slurm Factory is a **modern Python CLI tool** built with Typer that automates the building of **relocatable** Slurm workload manager packages using Docker containers and the Spack package manager. It features a **modular architecture** with comprehensive exception handling, intelligent caching, and portable package generation for HPC environments.

Or from source:

## Key Features

```shell-session

- 🏗️ **Modern Architecture**: Built with Typer CLI framework and modular Python designgit clone https://github.com/vantagecompute/vantage-cli

- 📦 **Relocatable Packages**: Runtime path configuration for cross-environment deploymentcd vantage-cli

- ⚡ **Intelligent Caching**: Multi-layer build caching for ultra-fast rebuildsuv sync

- 🔧 **Exception Handling**: Comprehensive error management with custom exception hierarchyuv run vantage --help

- 🧪 **Tested**: 100% test coverage with 112 passing tests using proper mocking```

- 🚀 **GPU Support**: CUDA-enabled builds for GPU-accelerated workloads

#### Authenticate

## Quick Start

Authenticate against the Vantage platform using the `login` command.

### Installation

```bash

```bashvantage login

# Install from PyPI (recommended)```

pip install slurm-factory

#### Create a Multipass Singlenode Cluster

# Or install with pipx for isolation

pipx install slurm-factory```bash

vantage cluster create my-slurm-multipass-cluster \

# Verify installation    --cloud localhost \

slurm-factory --help    --app slurm-multipass-localhost

``````



### Prerequisites#### Create a Slurm Cluster in LXD Containers using Juju



```bash```bash

# Install and configure Dockervantage cluster create my-slurm-lxd-cluster \

sudo apt install docker.io    --cloud localhost \

sudo usermod -aG docker $USER    --app slurm-juju-localhost

# Log out and back in for group changes to take effect```

```

#### Create a Slurm Cluster on MicroK8S

### Build Your First Relocatable Package

```bash

```bashvantage cluster create my-slurm-microk8s-cluster \

# Build latest Slurm with optimizations    --cloud localhost \

slurm-factory build --slurm-version 25.05    --app slurm-microk8s-localhost

```

# Build with GPU support

slurm-factory build --slurm-version 25.05 --gpu### Next Steps



# Build minimal configuration- [Installation Guide](./installation) – Install & Configure

slurm-factory build --slurm-version 25.05 --minimal- [Commands Reference](./commands) – Complete Command Reference

- [Private Installation Configuration](./private-vantage-installation) – Partner Vantage Deployment CLI Profile Configuration

# Show available options- [Notebooks](./notebooks) – Jupyterhub Notebook Server Lifecycle

slurm-factory build --help- [Deployment Applications](./deployment-applications) – Slurm Deployment Automation

```- [Usage Examples](./usage) – Practical Command Patterns

- [Architecture](./architecture) – Internals & Module Layout

### Deploy Anywhere- [Troubleshooting](./troubleshooting) – Common Issues and Solutions


```bash
# Standard deployment
sudo mkdir -p /opt/slurm
sudo tar -xzf ~/.slurm-factory/slurm-25.05-software.tar.gz -C /opt/slurm/

# Load module with default path
module load slurm/25.05

# Or deploy to custom location  
sudo tar -xzf ~/.slurm-factory/slurm-25.05-software.tar.gz -C /shared/apps/
export SLURM_INSTALL_PREFIX=/shared/apps/view
module load slurm/25.05
```

## Use Cases

- **HPC Cluster Deployment**: Standardized Slurm installations across heterogeneous clusters
- **Development Environments**: Quick Slurm setup for testing and development
- **Multi-Version Support**: Running different Slurm versions side-by-side
- **Performance Testing**: Optimized builds for specific hardware configurations
- **Container Deployment**: Portable packages for containerized HPC environments

## Architecture Overview

```
┌─────────────────┐    ┌──────────────┐    ┌─────────────────┐
│   slurm-factory │───▶│ Docker       │───▶│ Spack Build     │
│   CLI Tool      │    │ Container    │    │ Environment     │
└─────────────────┘    └──────────────┘    └─────────────────┘
                                                      │
                                                      ▼
┌─────────────────┐    ┌──────────────┐    ┌─────────────────┐
│ Target HPC      │◀───│ Portable     │◀───│ Optimized       │
│ Cluster         │    │ Packages     │    │ Slurm Build     │
└─────────────────┘    └──────────────┘    └─────────────────┘
```

## Package Information

| Build Type | Dependencies | Size | Build Time | Use Case |
|------------|-------------|------|------------|----------|
| **CPU-only** | ~45 packages | ~2-5GB | ~35 min | Production clusters |
| **GPU-enabled** | ~180 packages | ~15-25GB | ~75 min | GPU clusters |
| **Minimal** | ~20 packages | ~1-2GB | ~15 min | Development/testing |

## Latest Features

- **Multi-Version Support**: Build and deploy Slurm versions 25.05, 24.11, 23.11, 23.02
- **GPU Optimization**: Optional CUDA support for GPU-enabled HPC clusters  
- **Portable Packages**: Self-contained deployments with module system integration
- **Modern Architecture**: Docker containers with Spack package management
- **Performance Focused**: CPU-optimized builds with minimal package sizes

---

**Built with ❤️ by [Vantage Compute](https://vantagecompute.ai)**
