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

"""Slurm build process management."""

import logging
import subprocess
import uuid

import typer
from rich.console import Console
from typing_extensions import Annotated

from .constants import INSTANCE_NAME_PREFIX, SlurmVersion
from .exceptions import SlurmFactoryError
from .utils import create_slurm_package

logger = logging.getLogger(__name__)


def build(
    ctx: typer.Context,
    slurm_version: Annotated[
        SlurmVersion, typer.Option("--slurm-version", help="Slurm version to build")
    ] = SlurmVersion.v25_05,
    gpu: bool = False,
    additional_variants: str = "",
    minimal: bool = False,
    verify: bool = False,
):
    """Build a specific Slurm version in a Docker container."""
    console = Console()

    # Initialize settings and ensure cache directories exist
    settings = ctx.obj["settings"]
    verbose = ctx.obj["verbose"]

    logger.debug(
        f"Starting build with parameters: slurm_version={slurm_version.value}, "
        f"gpu={gpu}, minimal={minimal}, verify={verify}"
    )
    logger.debug(f"Verbose mode: {verbose}")

    settings.ensure_cache_dirs()
    logger.debug(f"Ensured cache directories exist at {settings.home_cache_dir}")

    # Check if Docker is available
    try:
        result = subprocess.run(
            ["docker", "version"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode != 0:
            console.print("[bold red]Docker is not running or not accessible[/bold red]")
            logger.error("Docker version check failed")
            raise SlurmFactoryError("Docker is not available. Please ensure Docker is installed and running.")
    except FileNotFoundError:
        console.print("[bold red]Docker is not installed[/bold red]")
        logger.error("Docker command not found")
        raise SlurmFactoryError("Docker is not installed. Please install Docker first.")
    except subprocess.TimeoutExpired:
        console.print("[bold red]Docker check timed out[/bold red]")
        logger.error("Docker version check timed out")
        raise SlurmFactoryError("Docker is not responding. Please check your Docker installation.")

    version = slurm_version.value
    console.print(f"Starting Slurm build process for version {version}")
    logger.debug(f"Building Slurm version {slurm_version.value}")

    # Generate unique container name for this build
    short_uuid = f"{uuid.uuid4()}"[:8]
    safe_version = version.replace(".", "-")
    container_name = f"{INSTANCE_NAME_PREFIX}-{safe_version}-{short_uuid}"
    image_tag = f"{INSTANCE_NAME_PREFIX}:build-{safe_version}-{short_uuid}"
    logger.debug(f"Generated container name: {container_name}")
    logger.debug(f"Generated image tag: {image_tag}")

    console.print(f"[bold blue]Building Docker image and container {container_name}...[/bold blue]")

    try:
        # Build and run the container - this will handle everything
        create_slurm_package(
            container_name=container_name,
            image_tag=image_tag,
            version=version,
            gpu_support=gpu,
            additional_variants=additional_variants,
            minimal=minimal,
            verify=verify,
            cache_dir=str(settings.home_cache_dir),
            verbose=verbose,
        )
        logger.debug("Slurm package creation completed")
        console.print("[bold green]✓ Slurm package created successfully[/bold green]")
    except SlurmFactoryError as e:
        logger.error(f"Failed to create Slurm package: {e}")
        console.print(f"[bold red]Failed to create Slurm package:[/bold red] {e}")
        # Container cleanup will be handled in the utils module
        console.print(f"[yellow]Build container {container_name} may be left running for debugging[/yellow]")
        raise

    logger.info(f"Build process completed successfully for Slurm {version}")
    console.print("[bold green]Build completed successfully![/bold green]")
