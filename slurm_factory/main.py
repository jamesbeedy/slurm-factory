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

"""Main typer app for slurm-factory."""

import logging
import subprocess
import sys

import typer
from rich.console import Console
from rich.markup import escape
from typing_extensions import Annotated

from slurm_factory.builder import SlurmVersion
from slurm_factory.builder import build as builder_build
from slurm_factory.config import Settings

# Configure logging following craft-providers pattern
app = typer.Typer(name="Slurm Factory", add_completion=True)


def setup_logging(verbose: bool = False):
    """Configure logging based on verbosity level."""
    if verbose:
        level = logging.DEBUG
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    else:
        level = logging.INFO
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    logging.basicConfig(
        level=level,
        format=format_string,
        stream=sys.stderr,
        force=True,  # Override any existing logging config
    )

    # Set specific loggers to appropriate levels
    if verbose:
        logging.getLogger("slurm_factory").setLevel(logging.DEBUG)
        logging.getLogger("craft_providers").setLevel(logging.DEBUG)
    else:
        logging.getLogger("slurm_factory").setLevel(logging.INFO)
        logging.getLogger("craft_providers").setLevel(logging.WARNING)


@app.callback()
def main(
    ctx: typer.Context,
    project_name: Annotated[
        str,
        typer.Option(
            "--project-name",
            envvar="IF_PROJECT_NAME",
            help="The LXD project in which resources are going to be created",
        ),
    ] = "slurm-factory",
    verbose: Annotated[bool, typer.Option("--verbose", "-v", help="Enable verbose output")] = False,
):
    """Handle global options for the application."""
    setup_logging(verbose=verbose)

    settings = Settings(project_name=project_name)

    ctx.ensure_object(dict)
    ctx.obj["project_name"] = project_name
    ctx.obj["verbose"] = verbose
    ctx.obj["settings"] = settings


@app.command("clean")
def clean(
    ctx: typer.Context,
    full_cleanup: Annotated[
        bool, typer.Option("--full", help="Remove Docker images in addition to containers")
    ] = False,
):
    """
    Clean up Docker containers and images from slurm-factory builds.

    By default, removes stopped containers but keeps images for faster rebuilds.
    Use --full to remove both containers and images.

    Examples:
        slurm-factory clean        # Remove stopped containers
        slurm-factory clean --full  # Remove containers and images

    """
    console = Console()
    logger = logging.getLogger(__name__)
    logger.info("Cleaning up Docker containers and images")

    try:
        # List all containers with slurm-factory prefix
        result = subprocess.run(
            ["docker", "ps", "-a", "--filter", "name=slurm-factory", "--format", "{{.Names}}"],
            capture_output=True,
            text=True,
            timeout=10,
        )

        if result.returncode != 0:
            console.print("[bold red]Failed to list Docker containers[/bold red]")
            return

        containers = [line.strip() for line in result.stdout.split("\n") if line.strip()]

        if not containers:
            console.print("[green]No slurm-factory containers found[/green]")
        else:
            console.print(f"[bold red]Removing {len(containers)} slurm-factory container(s):[/bold red]")
            for container_name in containers:
                console.print(f"  [red]🗑️  {container_name}[/red]")

            # Remove containers
            for container_name in containers:
                try:
                    logger.debug(f"Removing container: {container_name}")
                    subprocess.run(
                        ["docker", "rm", "-f", container_name],
                        capture_output=True,
                        text=True,
                        timeout=30,
                    )
                    console.print(f"  [green]✓[/green] Removed {container_name}")
                except Exception as e:
                    logger.error(f"Failed to remove container {container_name}: {e}")
                    console.print(f"  [red]✗[/red] Failed to remove {container_name}")

        # Clean up images if full cleanup requested
        if full_cleanup:
            console.print("\n[bold blue]Cleaning up Docker images...[/bold blue]")
            result = subprocess.run(
                [
                    "docker",
                    "images",
                    "--filter",
                    "reference=slurm-factory:*",
                    "--format",
                    "{{.Repository}}:{{.Tag}}",
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0:
                images = [line.strip() for line in result.stdout.split("\n") if line.strip()]

                if not images:
                    console.print("[green]No slurm-factory images found[/green]")
                else:
                    console.print(f"[bold red]Removing {len(images)} slurm-factory image(s):[/bold red]")
                    for image_name in images:
                        console.print(f"  [red]�️  {image_name}[/red]")

                    # Remove images
                    for image_name in images:
                        try:
                            logger.debug(f"Removing image: {image_name}")
                            subprocess.run(
                                ["docker", "rmi", "-f", image_name],
                                capture_output=True,
                                text=True,
                                timeout=60,
                            )
                            console.print(f"  [green]✓[/green] Removed {image_name}")
                        except Exception as e:
                            logger.error(f"Failed to remove image {image_name}: {e}")
                            console.print(f"  [red]✗[/red] Failed to remove {image_name}")

        console.print("\n[bold green]✓ Cleanup completed[/bold green]")

        if not full_cleanup and len(containers) > 0:
            console.print("[dim]Tip: Use [bold]--full[/bold] to also remove Docker images[/dim]")

    except FileNotFoundError:
        console.print("[bold red]Docker is not installed or not in PATH[/bold red]")
        logger.error("Docker command not found")
        raise typer.Exit(1)
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")
        console.print(f"[bold red]Error during cleanup: {escape(str(e))}[/bold red]")
        raise typer.Exit(1)


@app.command("build")
def build(
    ctx: typer.Context,
    slurm_version: Annotated[
        SlurmVersion, typer.Option("--slurm-version", help="Slurm version to build")
    ] = SlurmVersion.v25_05,
    gpu: Annotated[
        bool, typer.Option("--gpu", help="Enable GPU support (CUDA/ROCm) - creates larger packages")
    ] = False,
    additional_variants: Annotated[
        str, typer.Option("--additional-variants", help="Additional Spack variants to include")
    ] = "",
    minimal: Annotated[
        bool, typer.Option("--minimal", help="Build minimal Slurm only (no OpenMPI, smaller size)")
    ] = False,
    verify: Annotated[
        bool, typer.Option("--verify", help="Enable relocatability verification (for CI/testing)")
    ] = False,
    no_cache: Annotated[
        bool, typer.Option("--no-cache", help="Force a fresh build without using Docker cache")
    ] = False,
):
    """
    Build a specific Slurm version.

    Available versions: 25.05 (default), 24.11, 23.11, 23.02

    Build types:
    - Default: ~2-5GB, CPU-only with OpenMPI and standard features
    - --gpu: ~15-25GB, includes CUDA/ROCm support for GPU workloads
    - --minimal: ~1-2GB, basic Slurm only without OpenMPI or extra features
    - --verify: Enable relocatability verification for CI/testing
    - --no-cache: Force a fresh build without using Docker layer cache

    Each version includes:
    - Dynamic Spack configuration with relocatability features
    - Explicit compiler toolchains (toolchains)
    - Short install paths (install_tree.padded_length: 0)
    - System linkage validation (shared_linking.missing_library_policy: error)
    - Optional verification checks (--verify for CI)
    - Global patches (shared across versions)
    - Redistributable Lmod modules

    Examples:
        slurm-factory build                                    # Build default CPU version (25.05)
        slurm-factory build --slurm-version 24.11             # Build specific version
        slurm-factory build --gpu                             # Build with GPU support
        slurm-factory build --minimal                         # Build minimal version
        slurm-factory build --verify                          # Build with verification (CI)
        slurm-factory build --no-cache                        # Build without Docker cache

    """
    console = Console()

    if additional_variants is not None:
        console.print(
            f"[bold yellow]Including additional Spack variants: {additional_variants}[/bold yellow]"
        )
        console.print("[bold yellow]⚠️  Note: This may increase build time and image size.[/bold yellow]")
        if "+mcs" in additional_variants and slurm_version != SlurmVersion.v25_05:
            console.print("[bold error] 'mcs' variant is only supported in slurm > 25.05.[/bold error]")

    if gpu and minimal:
        console.print("[bold red]Error: --gpu and --minimal cannot be used together[/bold red]")
        raise typer.Exit(1)

    console.print(
        f"[bold green]Starting build for Slurm {slurm_version} "
        f"with additional variants: {additional_variants}[/bold green]"
    )
    if no_cache:
        console.print("[bold yellow]Building with --no-cache (fresh build)[/bold yellow]")

    builder_build(ctx, slurm_version, gpu, additional_variants, minimal, verify, no_cache)


if __name__ == "__main__":
    app()
