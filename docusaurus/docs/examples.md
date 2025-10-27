
# Slurm Factory Examples

This page contains practical examples demonstrating how to use Slurm Factory for various HPC deployment scenarios with the new Typer CLI.

## Basic Usage Examples

### Building Default Slurm Package
```bash
# Build latest Slurm (25.05) with CPU optimizations
slurm-factory build

# Equivalent explicit command
slurm-factory build --slurm-version 25.05
```

### Building Specific Versions
```bash
# Build Slurm 24.11
slurm-factory build --slurm-version 24.11

# Build Slurm 23.11
slurm-factory build --slurm-version 23.11

# Build legacy Slurm 23.02
slurm-factory build --slurm-version 23.02
```

### Build Type Examples

#### GPU-Enabled Builds
```bash
# Build with CUDA/ROCm support (~15-25GB)
slurm-factory build --gpu

# GPU build for specific version
slurm-factory build --slurm-version 24.11 --gpu
```

#### Minimal Builds
```bash
# Build minimal package without OpenMPI (~1-2GB)
slurm-factory build --minimal

# Minimal build for specific version
slurm-factory build --slurm-version 25.05 --minimal
```

#### Verification Builds (CI/Testing)
```bash
# Build with relocatability verification
slurm-factory build --verify

# Verification build with GPU support
slurm-factory build --verify --gpu
```

## Advanced Usage Examples

### Project Management
```bash
# Use custom LXD project name
slurm-factory --project-name my-hpc-project build

# Set project via environment variable
export IF_PROJECT_NAME=production-slurm
slurm-factory build --slurm-version 25.05
```

### Verbose Debugging
```bash
# Enable verbose output for debugging
slurm-factory --verbose build

# Verbose output with custom project
slurm-factory --verbose --project-name debug-builds build --minimal
```

### Build Management
```bash
# Clean build instances (keep base instances for speed)
slurm-factory clean

# Full cleanup (removes everything, slower next build)
slurm-factory clean --full

# Clean specific project
slurm-factory --project-name my-project clean --full
```

## Deployment Examples

### Standard Deployment
```bash
# Extract software package to /opt/slurm
sudo mkdir -p /opt/slurm
sudo tar -xzf ~/.slurm-factory/builds/slurm-25.05-software.tar.gz -C /opt/slurm/

# Extract module files
sudo tar -xzf ~/.slurm-factory/builds/slurm-25.05-module.tar.gz -C /usr/share/lmod/lmod/modulefiles/

# Load the module
module load slurm/25.05
```

### Custom Path Deployment
```bash
# Deploy to custom shared filesystem location
sudo mkdir -p /shared/apps/slurm
sudo tar -xzf ~/.slurm-factory/builds/slurm-25.05-software.tar.gz -C /shared/apps/slurm/

# Set runtime prefix override
export SLURM_INSTALL_PREFIX=/shared/apps/slurm/software
module load slurm/25.05
```

### Multi-Version Deployment
```bash
# Deploy multiple versions side-by-side
sudo tar -xzf ~/.slurm-factory/builds/slurm-25.05-software.tar.gz -C /opt/
sudo tar -xzf ~/.slurm-factory/builds/slurm-24.11-software.tar.gz -C /opt/

# Extract all module files
sudo tar -xzf ~/.slurm-factory/builds/slurm-25.05-module.tar.gz -C /usr/share/lmod/lmod/modulefiles/
sudo tar -xzf ~/.slurm-factory/builds/slurm-24.11-module.tar.gz -C /usr/share/lmod/lmod/modulefiles/

# List available versions
module avail slurm

# Load specific version
module load slurm/24.11
```

## CI/CD Integration Examples

### GitHub Actions
```yaml
name: Build Slurm Package
on: [push, pull_request]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup LXD
        run: |
          sudo snap install lxd
          sudo lxd init --auto
      
      - name: Install Slurm Factory
        run: pip install slurm-factory
      
      - name: Build and Verify Slurm Package
        run: |
          slurm-factory --verbose build --verify
      
      - name: Test Package
        run: |
          # Custom package validation
          tar -tzf ~/.slurm-factory/builds/slurm-*-software.tar.gz | head -10
```

### Docker Integration
```dockerfile
FROM ubuntu:24.04

# Install dependencies
RUN apt-get update && apt-get install -y python3-pip

# Install Slurm Factory
RUN pip install slurm-factory

# Setup LXD (requires privileged container)
RUN snap install lxd

# Build script
COPY build-slurm.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/build-slurm.sh

CMD ["/usr/local/bin/build-slurm.sh"]
```

## Error Handling Examples

### Build Error Recovery
```bash
# If build fails, try cleaning first
slurm-factory clean
slurm-factory build --slurm-version 25.05

# For persistent issues, full cleanup
slurm-factory clean --full
slurm-factory --verbose build --slurm-version 25.05
```

### Project Conflicts
```bash
# Check for existing projects
lxc project list

# Use isolated project for testing
slurm-factory --project-name test-builds build --minimal

# Clean up test project
slurm-factory --project-name test-builds clean --full
```

## Performance Optimization Examples

### Leveraging Build Cache
```bash
# First build (45-90 minutes)
time slurm-factory build --slurm-version 25.05

# Subsequent builds with cache (5-15 minutes)
time slurm-factory build --slurm-version 25.05 --gpu
time slurm-factory build --slurm-version 24.11
```

### Parallel Project Builds
```bash
# Build multiple versions in parallel using separate projects
slurm-factory --project-name build-25-05 build --slurm-version 25.05 &
slurm-factory --project-name build-24-11 build --slurm-version 24.11 &
wait

# Clean all projects
slurm-factory --project-name build-25-05 clean --full
slurm-factory --project-name build-24-11 clean --full
```

## Python API Examples

### Basic Python Usage
```python
from slurm_factory.builder import build
from slurm_factory.constants import SlurmVersion
from slurm_factory.config import Settings
import typer

# Setup context
ctx = typer.Context(typer.Typer())
ctx.obj = {
    "settings": Settings(),
    "project_name": "my-python-project"
}

# Build programmatically
try:
    build(
        ctx=ctx,
        slurm_version=SlurmVersion.v25_05,
        gpu=False,
        minimal=False,
        verify=True,
        base_only=False
    )
    print("Build completed successfully!")
except Exception as e:
    print(f"Build failed: {e}")
```

### Configuration Management
```python
from slurm_factory.config import Settings

# Initialize with custom project
settings = Settings(project_name="production-slurm")

# Ensure cache directories exist
settings.ensure_cache_dirs()

print(f"Cache directory: {settings.home_cache_dir}")
print(f"Project name: {settings.project_name}")
```

For more detailed documentation, please refer to our [API Reference](/slurm-factory/api-reference/) and [Architecture Guide](/slurm-factory/architecture/).
