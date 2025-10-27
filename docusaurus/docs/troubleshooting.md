
# Troubleshooting Guide

Common issues and solutions when using slurm-factory with the modern Typer CLI.

## CLI Command Issues

### Command Not Found

**Problem**: `slurm-factory` command not found after installation

**Solution**:
```bash
# If installed with pip --user
export PATH=$PATH:~/.local/bin

# Or use python module directly
python -m slurm_factory --help

# For pipx installations, ensure path is set
pipx ensurepath
```

### Wrong Command Syntax

**Problem**: Using old command format

**Old (incorrect)**:
```bash
uv run slurm-factory build 25.05 --gpu
```

**New (correct)**:
```bash
slurm-factory build --slurm-version 25.05 --gpu
```

## Installation Issues

### Docker Permission Errors

**Problem**: Permission denied when accessing Docker daemon
```
Error: Got permission denied while trying to connect to the Docker daemon socket
```

**Solution**:
```bash
# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Verify Docker access
docker ps
```

### UV Not Found

**Problem**: `uv` command not found after installation

**Solution**:
```bash
# Reload shell configuration
source ~/.bashrc

# Or reinstall UV
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Build Issues

### Out of Memory Errors

**Problem**: Build fails with memory errors

**Solutions**:
```bash
# Monitor Docker container memory usage
docker stats

# Reduce parallel jobs
export SPACK_BUILD_JOBS=2
```

### Network/Download Issues

**Problem**: Downloads fail during build

**Solutions**:
```bash
# Test connectivity
ping -c 3 github.com

# Configure proxy (if needed)
export http_proxy=http://proxy.company.com:8080
```

### Disk Space Issues

**Problem**: No space left on device

**Solutions**:
```bash
# Check space usage
df -h ~/.slurm-factory/

# Clean old builds
rm -rf ~/.slurm-factory/builds/old-version/
```

## Runtime Issues

### Module Not Found

**Problem**: Module system can't find Slurm modules

**Solutions**:
```bash
# Check module path
echo $MODULEPATH

# Add module directory
export MODULEPATH=/opt/modules:$MODULEPATH
```

### Command Not Found

**Problem**: Slurm commands not found after loading module

**Solutions**:
```bash
# Check module is loaded
module list

# Reload module
module unload slurm/25.05
module load slurm/25.05
```

### Library Errors

**Problem**: Library loading errors

**Solutions**:
```bash
# Check library path
echo $LD_LIBRARY_PATH | grep slurm

# Update library cache
sudo ldconfig
```

## Getting Help

### Bug Reports

Include system information when reporting issues:

```bash
# System information
uname -a
lxd --version
python3 --version

# Slurm Factory logs
cat ~/.slurm-factory/logs/latest.log
```

### Community Support

- **GitHub Issues**: [Report bugs](https://github.com/vantagecompute/slurm-factory/issues)
- **Discussions**: [Get help](https://github.com/vantagecompute/slurm-factory/discussions)
- **Documentation**: [Full docs](https://vantagecompute.github.io/slurm-factory)

