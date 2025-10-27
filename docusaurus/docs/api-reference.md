
# API Reference

Complete reference for the slurm-factory Python API and command-line interface.

## Command Line Interface

The slurm-factory CLI is built with [Typer](https://typer.tiangolo.com/) and provides a modern, user-friendly interface for building Slurm packages.

### Global Options

All commands support these global options:

```bash
slurm-factory [GLOBAL_OPTIONS] COMMAND [COMMAND_OPTIONS]
```

**Global Options:**
- `--project-name TEXT`: LXD project name (default: "slurm-factory", env: `IF_PROJECT_NAME`)
- `--verbose`, `-v`: Enable verbose output and debug logging
- `--help`: Show help message

### `slurm-factory build`

Build a Slurm package with specified version and options.

```bash
slurm-factory build [OPTIONS]
```

**Options:**
- `--slurm-version [25.05|24.11|23.11|23.02]`: Slurm version to build (default: 25.05)
- `--gpu / --no-gpu`: Enable GPU support (CUDA/ROCm) - creates larger packages (default: False)
- `--minimal / --no-minimal`: Build minimal Slurm only (no OpenMPI, smaller size) (default: False)
- `--verify / --no-verify`: Enable relocatability verification for CI/testing (default: False)
- `--base-only / --no-base-only`: Only build base images (no extra features) (default: False)
- `--help`: Show help message

**Build Types:**
- **Default**: ~2-5GB, CPU-only with OpenMPI and standard features
- **GPU (`--gpu`)**: ~15-25GB, includes CUDA/ROCm support for GPU workloads
- **Minimal (`--minimal`)**: ~1-2GB, basic Slurm only without OpenMPI or extra features

**Note:** `--gpu` and `--minimal` cannot be used together.

**Examples:**
```bash
# Build default CPU version (25.05)
slurm-factory build

# Build specific version
slurm-factory build --slurm-version 24.11

# Build with GPU support
slurm-factory build --gpu

# Build minimal version
slurm-factory build --minimal

# Build with verification (CI)
slurm-factory build --verify

# Verbose build with custom project
slurm-factory --verbose --project-name my-project build --slurm-version 25.05
```

### `slurm-factory clean`

Clean up LXD instances from the project.

```bash
slurm-factory clean [OPTIONS]
```

**Options:**
- `--full / --no-full`: Completely delete the LXD project (default: False)
- `--help`: Show help message

**Behavior:**
- **Default**: Cleans build instances, keeps base instances for faster subsequent builds
- **Full (`--full`)**: Completely deletes the LXD project including base instances

**Examples:**
```bash
# Clean build instances, keep base instances
slurm-factory clean

# Completely delete the LXD project
slurm-factory clean --full

# Clean with custom project
slurm-factory --project-name my-project clean --full
```

## Python API

### Module Structure

The slurm-factory Python package is organized into the following modules:

```python
import slurm_factory
from slurm_factory import builder, config, constants, exceptions, spack_yaml, utils
```

### Core Enums

#### `SlurmVersion`

Enumeration of supported Slurm versions.

```python
from slurm_factory.constants import SlurmVersion

# Available versions
SlurmVersion.v25_05  # "25.05"
SlurmVersion.v24_11  # "24.11" 
SlurmVersion.v23_11  # "23.11"
SlurmVersion.v23_02  # "23.02"
```

### Configuration

#### `Settings`

Configuration management using Pydantic.

```python
from slurm_factory.config import Settings

settings = Settings()
print(settings.project_name)     # Default: "slurm-factory"
print(settings.home_cache_dir)   # Cache directory path

# Ensure cache directories exist
settings.ensure_cache_dirs()
```

### Builder Module

#### `build()` Function

Main build function (typically called via CLI).

```python
from slurm_factory.builder import build
import typer

# Build context (normally provided by CLI)
ctx = typer.Context(typer.Typer())
ctx.obj = {
    "settings": Settings(),
    "project_name": "slurm-factory"
}

# Build with options
build(
    ctx=ctx,
    slurm_version=SlurmVersion.v25_05,
    gpu=False,
    minimal=False,
    verify=False,
    base_only=False
)
```

### Exception Handling

#### Custom Exceptions

```python
from slurm_factory.exceptions import (
    SlurmFactoryError,
    ConfigurationError,
    BuildError,
    LXDError,
    SpackError
)

try:
    # Slurm Factory operations
    pass
except BuildError as e:
    print(f"Build failed: {e}")
except LXDError as e:
    print(f"LXD operation failed: {e}")
except SlurmFactoryError as e:
    print(f"General error: {e}")
```

### Spack Configuration

#### `generate_spack_yaml()` Function

Generate dynamic Spack configuration based on build options.

```python
from slurm_factory.spack_yaml import generate_spack_yaml
from slurm_factory.constants import SlurmVersion

# Generate configuration
config = generate_spack_yaml(
    slurm_version=SlurmVersion.v25_05,
    gpu_enabled=False,
    minimal=False
)

print(config)  # YAML configuration as string
```

### Utility Functions

#### LXD Operations

```python
from slurm_factory.utils import (
    get_base_instance_name,
    set_profile,
    create_buildcache_from_base_instance,
    create_slurm_package
)

# Get standardized instance name
name = get_base_instance_name(SlurmVersion.v25_05, gpu=False, minimal=False)
print(name)  # "slurm-factory-base-25.05"

# Set LXD profile for build optimization
set_profile("default", "slurm-factory", "/path/to/cache")
```

### Constants

#### Build Configuration

```python
from slurm_factory.constants import (
    INSTANCE_NAME_PREFIX,
    SPACK_VIEW_SCRIPT,
    SLURM_PACKAGES,
    EXTERNAL_BUILD_TOOLS
)

print(INSTANCE_NAME_PREFIX)  # "slurm-factory"
print(SLURM_PACKAGES)        # Dict of Slurm package specs
```

## Error Handling

All functions raise specific exceptions for different error conditions:

- `SlurmFactoryError`: Base exception for all library errors
- `ConfigurationError`: Configuration-related errors
- `BuildError`: Build process failures
- `LXDError`: LXD operation failures  
- `SpackError`: Spack operation failures

Example error handling:

```python
from slurm_factory.exceptions import BuildError, LXDError
from slurm_factory.builder import build

try:
    build(ctx, SlurmVersion.v25_05)
except LXDError as e:
    print(f"LXD setup failed: {e}")
except BuildError as e:
    print(f"Build process failed: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Environment Variables

- `IF_PROJECT_NAME`: Default LXD project name (default: "slurm-factory")

## Exit Codes

- `0`: Success
- `1`: General error (build failure, configuration error, etc.)

## Logging

The library uses Python's standard logging module. Enable debug logging with:

```bash
slurm-factory --verbose build
```

Or programmatically:

```python
import logging
logging.getLogger("slurm_factory").setLevel(logging.DEBUG)
```
        """
    
    def build_slurm_package(
        self, 
        slurm_version: str, 
        gpu: bool = False
    ) -> BuildResult:
        """Build a Slurm package.
        
        Args:
            slurm_version: Version of Slurm to build
            gpu: Enable GPU support
            
        Returns:
            BuildResult with success status and package paths
            
        Raises:
            BuildError: If build fails
            ContainerError: If container operations fail
        """
```

**Example Usage:**
```python
from slurm_factory.builder import SlurmBuilder

# Create builder
builder = SlurmBuilder()

# Build package
result = builder.build_slurm_package("25.05", gpu=False)

if result.success:
    print(f"Built packages: {result.packages}")
else:
    print(f"Build failed: {result.errors}")
```

#### `SlurmVersion`

Enum for supported Slurm versions.

```python
from slurm_factory.constants import SlurmVersion

class SlurmVersion(str, Enum):
    V25_05 = "25.05"
    V24_11 = "24.11"
    V24_05 = "24.05"
    V23_11 = "23.11"
    V23_02 = "23.02"
```

#### `BuildResult`

Result object returned by build operations.

```python
@dataclass
class BuildResult:
    success: bool
    packages: List[Path]
    build_time: timedelta
    errors: List[str]
    slurm_version: str
    gpu_enabled: bool
```

### Configuration

#### `Config`

Configuration management class.

```python
from slurm_factory.config import Config

class Config:
    @property
    def build_dir(self) -> Path:
        """Build directory path."""
    
    @property
    def cache_dir(self) -> Path:
        """Cache directory path."""
    
    @property
    def output_dir(self) -> Path:
        """Output directory path."""
    
    def get_container_config(self) -> ContainerConfig:
        """Get container configuration."""
    
    def get_spack_config(self, version: str, gpu: bool) -> SpackConfig:
        """Get Spack configuration for version."""
```

### Constants

#### Version Mappings

```python
from slurm_factory.constants import SLURM_VERSIONS

# Dictionary mapping versions to download URLs and hashes
SLURM_VERSIONS = {
    "25.05": {
        "url": "https://github.com/SchedMD/slurm/archive/refs/tags/slurm-25-05.tar.gz",
        "hash": "sha256:...",
        "spack_spec": "slurm@25.05"
    },
    # ... other versions
}
```

#### Script Templates

```python
from slurm_factory.constants import (
    SPACK_INSTALL_SCRIPT,
    SLURM_BUILD_SCRIPT,
    PACKAGE_CREATION_SCRIPT
)

# Access script templates for customization
script = SPACK_INSTALL_SCRIPT.substitute(
    spack_version="v0.20.1",
    python_version="3.11"
)
```

### Exceptions

#### `BuildError`

Base exception for build-related errors.

```python
class BuildError(Exception):
    """Base exception for build errors."""
    
    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(message)
        self.details = details or {}
```

#### `ContainerError`

Exception for container-related errors.

```python
class ContainerError(BuildError):
    """Exception for container operations."""
    
    def __init__(self, message: str, container_id: Optional[str] = None):
        super().__init__(message)
        self.container_id = container_id
```

#### `SpackError`

Exception for Spack-related errors.

```python
class SpackError(BuildError):
    """Exception for Spack operations."""
    
    def __init__(self, message: str, command: Optional[str] = None):
        super().__init__(message)
        self.command = command
```

### Utilities

#### Package Management

```python
from slurm_factory.utils import (
    list_built_packages,
    clean_build_artifacts,
    validate_package
)

def list_built_packages() -> List[PackageInfo]:
    """List all built packages."""

def clean_build_artifacts(keep_cache: bool = True) -> CleanResult:
    """Clean build artifacts."""

def validate_package(package_path: Path) -> ValidationResult:
    """Validate package integrity."""
```

#### Container Utilities

```python
from slurm_factory.container import (
    list_containers,
    cleanup_containers,
    get_container_info
)

def list_containers() -> List[ContainerInfo]:
    """List active build containers."""

def cleanup_containers() -> int:
    """Clean up orphaned containers."""

def get_container_info(container_id: str) -> ContainerInfo:
    """Get container information."""
```

## Data Structures

### Configuration Objects

#### `ContainerConfig`

```python
@dataclass
class ContainerConfig:
    image: str = "ubuntu:22.04"
    cpu_limit: Optional[str] = None
    memory_limit: str = "16GB"
    swap_limit: bool = False
    network: str = "default"
    storage_pool: str = "default"
```

#### `SpackConfig`

```python
@dataclass
class SpackConfig:
    version: str
    install_dir: Path
    cache_dir: Path
    build_jobs: int
    specs: List[str]
    variants: Dict[str, str]
```

#### `PackageInfo`

```python
@dataclass
class PackageInfo:
    slurm_version: str
    gpu_enabled: bool
    build_date: datetime
    software_package: Path
    module_package: Path
    size_mb: int
```

### Result Objects

#### `ValidationResult`

```python
@dataclass
class ValidationResult:
    valid: bool
    errors: List[str]
    warnings: List[str]
    package_info: Optional[PackageInfo] = None
```

#### `CleanResult`

```python
@dataclass
class CleanResult:
    files_removed: int
    space_freed_mb: int
    errors: List[str]
```

## Environment Variables

### Configuration Variables

```bash
# Build configuration
export SLURM_FACTORY_BUILD_DIR="$HOME/.slurm-factory"
export SLURM_FACTORY_CACHE_DIR="$HOME/.slurm-factory/cache"
export SLURM_FACTORY_OUTPUT_DIR="$HOME/.slurm-factory/builds"

# Container configuration
export SLURM_FACTORY_CONTAINER_CPU="8"
export SLURM_FACTORY_CONTAINER_MEMORY="16GB"
export SLURM_FACTORY_CONTAINER_IMAGE="ubuntu:22.04"

# Spack configuration
export SLURM_FACTORY_SPACK_JOBS="8"
export SLURM_FACTORY_SPACK_CACHE="$HOME/.slurm-factory/spack-cache"

# Logging
export SLURM_FACTORY_LOG_LEVEL="INFO"
export SLURM_FACTORY_LOG_FILE="$HOME/.slurm-factory/logs/slurm-factory.log"
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0    | Success |
| 1    | General error |
| 2    | Invalid arguments |
| 3    | Container error |
| 4    | Build error |
| 5    | Package error |
| 6    | Configuration error |

## Examples

### Basic Usage

```python
#!/usr/bin/env python3
"""Example: Build and deploy Slurm package."""

from pathlib import Path
from slurm_factory.builder import SlurmBuilder
from slurm_factory.utils import validate_package

def main():
    # Initialize builder
    builder = SlurmBuilder(output_dir=Path("/custom/output"))
    
    # Build package
    result = builder.build_slurm_package("25.05", gpu=False)
    
    if not result.success:
        print(f"Build failed: {result.errors}")
        return 1
    
    # Validate packages
    for package in result.packages:
        validation = validate_package(package)
        if not validation.valid:
            print(f"Package validation failed: {validation.errors}")
            return 1
    
    print(f"Successfully built {len(result.packages)} packages")
    print(f"Build time: {result.build_time}")
    return 0

if __name__ == "__main__":
    exit(main())
```

### Custom Configuration

```python
#!/usr/bin/env python3
"""Example: Custom build configuration."""

from slurm_factory.builder import SlurmBuilder
from slurm_factory.config import Config, ContainerConfig, SpackConfig

def main():
    # Custom container configuration
    container_config = ContainerConfig(
        cpu_limit="16",
        memory_limit="32GB",
        swap_limit=False
    )
    
    # Custom Spack configuration
    spack_config = SpackConfig(
        build_jobs=16,
        variants={"slurm": "+pmix +hwloc +numa"}
    )
    
    # Initialize with custom config
    config = Config()
    config.container_config = container_config
    config.spack_config = spack_config
    
    builder = SlurmBuilder(config=config)
    
    # Build with custom configuration
    result = builder.build_slurm_package("25.05", gpu=True)
    
    return 0 if result.success else 1

if __name__ == "__main__":
    exit(main())
```

