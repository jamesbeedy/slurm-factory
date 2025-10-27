
# Slurm Factory Overview

Slurm Factory is a **modern Python CLI tool** built with Typer that automates building optimized, relocatable Slurm workload manager packages using LXD containers and the Spack package manager. It features a modular architecture with comprehensive exception handling and intelligent caching.

## What is Slurm Factory?

Slurm Factory simplifies the complex process of building and packaging Slurm for HPC environments by:

- **Modern CLI Interface** with Typer framework providing auto-completion and rich help
- **Modular Architecture** with comprehensive error handling and type safety
- **Automating the build process** with one-command package creation
- **Creating relocatable packages** that can be deployed to any filesystem path
- **Optimizing performance** with CPU-specific optimizations and optional GPU support
- **Ensuring reproducibility** through container isolation and version-controlled dependencies
- **Supporting multiple versions** of Slurm (25.05, 24.11, 23.11, 23.02)

## Key Features

### 🏗️ **Modern Python Architecture**
- **Typer CLI**: Auto-completion, rich help, and type-safe command validation
- **Pydantic Configuration**: Type-safe settings with environment variable support
- **Custom Exception Hierarchy**: Structured error handling with actionable messages
- **Rich Console Output**: Colored progress indicators and user-friendly status

### 📦 **Relocatable Packages**
- **Runtime Path Configuration**: Deploy to any filesystem location
- **Environment Variable Overrides**: Customize installation paths at module load time
- **Portable Modules**: LMod modules that work across different environments
- **Self-Contained**: No external dependencies required at runtime

### ⚡ **Intelligent Build System**
- **Multi-Layer Caching**: Binary packages, source archives, and compiler cache
- **Container Optimization**: Base image reuse and persistent cache mounts
- **Fast Rebuilds**: 5-15 minutes for subsequent builds (vs 45-90 minutes initial)
- **Dependency Classification**: External tools vs runtime libraries for optimal sizing

### 🔧 **Comprehensive Exception Handling**
- **SlurmFactoryError**: Base exception with context-aware error messages
- **Specific Error Types**: LXD, build, and configuration-specific exceptions
- **Debugging Support**: Verbose logging and detailed error context
- **Recovery Guidance**: Actionable solutions for common issues

## Package Types

| Type | Size | Features | Use Case |
|------|------|----------|----------|
| **Default** | 2-5GB | CPU-optimized with OpenMPI | Standard HPC clusters |
| **GPU** | 15-25GB | CUDA/ROCm support | GPU-accelerated workloads |
| **Minimal** | 1-2GB | Basic Slurm only | Resource-constrained environments |

## CLI Examples

```bash
# Build latest Slurm with default settings
slurm-factory build

# Build with GPU support and verbose output
slurm-factory --verbose build --gpu

# Build specific version with custom project
slurm-factory --project-name production build --slurm-version 24.11

# Clean up build artifacts
slurm-factory clean --full
```

## Use Cases

- **Research Computing Centers**: Standardize Slurm deployments across multiple clusters
- **Cloud HPC Providers**: Rapidly provision clusters with consistent software stacks  
- **Educational Institutions**: Provide reproducible HPC environments for teaching
- **Industry HPC**: Deploy compliance-ready solutions with full audit trails
- **CI/CD Pipelines**: Automated testing and validation of HPC software stacks

## Next Steps

- [Installation Guide](/slurm-factory/installation/) - Get started with Slurm Factory
- [Architecture](/slurm-factory/architecture/) - Learn about the modular design
- [Examples](/slurm-factory/examples/) - Practical usage scenarios and patterns
- [API Reference](/slurm-factory/api-reference/) - Complete CLI and Python API documentation
