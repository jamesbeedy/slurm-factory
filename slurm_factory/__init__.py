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

"""
Slurm Factory - Modern Python CLI for Building Relocatable Slurm Packages.

A comprehensive tool for building optimized, relocatable Slurm workload manager
packages using Docker containers and the Spack package manager. Features a modern
Typer CLI interface, comprehensive exception handling, and intelligent caching.

Main modules:
- main: Typer CLI application with global options
- builder: Build orchestration and Docker container management
- config: Pydantic settings and cache management  
- constants: Enums, templates, and build configuration
- spack_yaml: Dynamic Spack configuration generation
- utils: Docker operations and package creation utilities
- exceptions: Custom exception hierarchy
"""
import importlib.metadata

from slurm_factory.builder import build
from slurm_factory.config import Settings
from slurm_factory.constants import SlurmVersion
from slurm_factory.exceptions import (
    SlurmFactoryError,
    SlurmFactoryStreamExecError,
    SlurmFactoryInstanceCreationError,
)
from slurm_factory.main import app
from slurm_factory.spack_yaml import generate_spack_config, generate_yaml_string

__version__ = importlib.metadata.version("slurm-factory")
__author__ = "Vantage Compute Corporation"
__email__ = "info@vantagecompute.ai"

__all__ = [
    # Main API
    "app",
    "build",
    "Settings",
    "SlurmVersion",
    "generate_spack_config",
    "generate_yaml_string",
    # Exceptions
    "SlurmFactoryError",
    "SlurmFactoryStreamExecError",
    "SlurmFactoryInstanceCreationError",
    # Version info
    "__version__",
    "__author__",
    "__email__",
]