---
title: "Slurm Factory - Modern HPC Cluster Builder"
description: "Build optimized Slurm packages using Docker containers and Spack package manager"
slug: /
---

# Slurm Factory Documentation

Slurm Factory is a **modern Python CLI tool** built with Typer that automates the building of **relocatable** Slurm workload manager packages using Docker containers and the Spack package manager. It features a **modular architecture** with comprehensive exception handling, intelligent caching, and portable package generation for HPC environments.

## Key Features

- 🏗️ **Modern Architecture**: Built with Typer CLI framework and modular Python design
- 📦 **Relocatable Packages**: Runtime path configuration for cross-environment deployment
- ⚡ **Intelligent Caching**: Multi-layer build caching for ultra-fast rebuilds
- 🔧 **Exception Handling**: Comprehensive error management with custom exception hierarchy
- 🧪 **Tested**: 100% test coverage with 112 passing tests
- 🚀 **GPU Support**: CUDA-enabled builds for GPU-accelerated workloads

## Quick Start

### Installation

```bash
# Install from PyPI (recommended)
pip install slurm-factory

# Or install with pipx for isolation
pipx install slurm-factory

# Verify installation
slurm-factory --help
```

### Prerequisites

```bash
# Install and configure Docker
sudo apt install docker.io
sudo usermod -aG docker $USER
# Log out and back in for group changes to take effect
```

### Build Your First Relocatable Package

```bash
# Build latest Slurm with optimizations
slurm-factory build --slurm-version 25.05

# Build with GPU support
slurm-factory build --slurm-version 25.05 --gpu

# Build minimal configuration
slurm-factory build --slurm-version 25.05 --minimal

# Show available options
slurm-factory build --help
```

### Deploy Anywhere

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
