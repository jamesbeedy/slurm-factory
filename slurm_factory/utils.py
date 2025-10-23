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

"""Utils used throughout the slurm-factory package."""

import logging
import subprocess
from pathlib import Path

from rich.console import Console
from rich.markup import escape

from .constants import (
    get_dockerfile,
    get_packager_dockerfile,
)
from .exceptions import SlurmFactoryError, SlurmFactoryStreamExecError
from .spack_yaml import generate_yaml_string

# Set up logging following craft-providers pattern
logger = logging.getLogger(__name__)
console = Console()


def _build_docker_image(
    image_tag: str,
    dockerfile_content: str,
    cache_dir: str,
    verbose: bool = False,
    no_cache: bool = False,
    target: str = "",
) -> None:
    """
    Build a Docker image from a Dockerfile string.

    Args:
        image_tag: Tag for the Docker image
        dockerfile_content: Complete Dockerfile as a string
        cache_dir: Host directory for cache mounts
        verbose: Whether to show detailed output
        no_cache: Force a fresh build without using Docker cache
        target: Build target stage in multi-stage builds (e.g., "builder")

    """
    console.print(f"[bold blue]Building Docker image {image_tag}...[/bold blue]")
    logger.debug(f"Building Docker image: {image_tag}")
    logger.debug(f"Dockerfile size: {len(dockerfile_content)} characters")
    
    if no_cache:
        logger.debug("Building with --no-cache flag")
        console.print("[bold yellow]Building without cache (this may take longer)[/bold yellow]")
    
    if target:
        logger.debug(f"Building target stage: {target}")
        console.print(f"[dim]Building target stage: {target}[/dim]")

    process = None
    try:
        # Use docker build with stdin for the Dockerfile
        cmd = [
            "docker",
            "build",
            "-t",
            image_tag,
            "-f",
            "-",  # Read Dockerfile from stdin
            ".",  # Build context (we don't actually use files from here)
        ]
        
        # Add --no-cache flag if requested
        if no_cache:
            cmd.insert(2, "--no-cache")
        
        # Add --target flag if specified
        if target:
            cmd.extend(["--target", target])

        if verbose:
            logger.debug(f"Docker build command: {' '.join(cmd)}")
            console.print(f"[dim]$ {' '.join(cmd)}[/dim]")

        # Stream output to terminal in real-time
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,  # Merge stderr into stdout
            text=True,
            bufsize=1,  # Line buffered
        )

        # Write Dockerfile to stdin
        if process.stdin:
            process.stdin.write(dockerfile_content)
            process.stdin.close()

        # Stream output line by line
        if process.stdout:
            for line in process.stdout:
                line = line.rstrip()
                if line:
                    console.print(f"  {escape(line)}")
                    logger.debug(f"Docker build: {line}")

        # Wait for process to complete
        returncode = process.wait(timeout=600)

        if returncode != 0:
            msg = f"Docker image build failed with exit code {returncode}"
            logger.error(msg)
            console.print(f"[bold red]{msg}[/bold red]")
            raise SlurmFactoryError(msg)

        console.print(f"[bold green]✓ Docker image {image_tag} built successfully[/bold green]")
        logger.debug("Docker image built successfully")

    except subprocess.TimeoutExpired:
        msg = "Docker image build timed out"
        logger.error(msg)
        console.print(f"[bold red]{msg}[/bold red]")
        if process:
            process.kill()
        raise SlurmFactoryError(msg)
    except Exception as e:
        msg = f"Failed to build Docker image: {e}"
        logger.error(msg)
        console.print(f"[bold red]{escape(msg)}[/bold red]")
        raise SlurmFactoryError(msg)


def _remove_old_docker_image(image_tag: str, verbose: bool = False) -> None:
    """
    Remove an old Docker image if it exists.

    Args:
        image_tag: Tag of the image to remove
        verbose: Whether to show detailed output

    """
    logger.debug(f"Checking for existing Docker image: {image_tag}")

    try:
        # Check if image exists
        result = subprocess.run(
            ["docker", "images", "-q", image_tag],
            capture_output=True,
            text=True,
            timeout=10,
        )

        if result.stdout.strip():
            # Image exists, remove it
            console.print(f"[bold yellow]Removing old Docker image: {image_tag}[/bold yellow]")
            remove_result = subprocess.run(
                ["docker", "rmi", "-f", image_tag],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if remove_result.returncode == 0:
                console.print(f"[bold green]✓ Removed old Docker image[/bold green]")
                logger.debug(f"Removed Docker image: {image_tag}")
            else:
                logger.warning(f"Failed to remove Docker image: {remove_result.stderr}")
        else:
            logger.debug(f"No existing Docker image found for: {image_tag}")

    except Exception as e:
        # Don't fail the build if we can't remove the old image
        logger.warning(f"Could not remove old Docker image: {e}")
        if verbose:
            console.print(f"[dim]Warning: Could not remove old image: {escape(str(e))}[/dim]")


def _clear_cache_directory(cache_dir: str, verbose: bool = False) -> None:
    """
    Clear the cache directory to force a completely fresh build.

    Args:
        cache_dir: Path to the cache directory to clear
        verbose: Whether to show detailed output

    """
    console.print("[bold yellow]Clearing cache directory for fresh build...[/bold yellow]")
    logger.debug(f"Clearing cache directory: {cache_dir}")

    import shutil

    cache_path = Path(cache_dir)
    
    if not cache_path.exists():
        logger.debug(f"Cache directory does not exist: {cache_dir}")
        return

    try:
        # Remove all contents but keep the directory
        for item in cache_path.iterdir():
            if item.is_file():
                item.unlink()
                if verbose:
                    console.print(f"[dim]Removed file: {item.name}[/dim]")
            elif item.is_dir():
                shutil.rmtree(item)
                if verbose:
                    console.print(f"[dim]Removed directory: {item.name}[/dim]")
        
        console.print(f"[bold green]✓ Cleared cache directory: {cache_dir}[/bold green]")
        logger.debug("Cache directory cleared successfully")

    except Exception as e:
        msg = f"Failed to clear cache directory: {e}"
        logger.error(msg)
        console.print(f"[bold red]{escape(msg)}[/bold red]")
        raise SlurmFactoryError(msg)




def create_slurm_package(
    container_name: str,
    image_tag: str,
    version: str = "25.05",
    gpu_support: bool = False,
    additional_variants: str = "",
    minimal: bool = False,
    verify: bool = False,
    cache_dir: str = "",
    verbose: bool = False,
    no_cache: bool = False,
) -> None:
    """Create slurm package in a Docker container using a two-stage build."""
    console.print("[bold blue]Creating slurm package in Docker container...[/bold blue]")

    logger.debug(
        f"Building Slurm package: version={version}, gpu={gpu_support}, minimal={minimal}, verify={verify}, no_cache={no_cache}"
    )

    builder_image_tag = f"{image_tag}-builder"
    packager_image_tag = f"{image_tag}-packager"

    try:
        # If no_cache is enabled, clean up everything first
        if no_cache:
            console.print("[bold yellow]🗑️  Performing fresh build - cleaning all caches...[/bold yellow]")
            
            # Remove old Docker images
            _remove_old_docker_image(image_tag, verbose=verbose)
            _remove_old_docker_image(builder_image_tag, verbose=verbose)
            _remove_old_docker_image(packager_image_tag, verbose=verbose)
            
            # Clear Docker build cache
            console.print("[dim]Pruning Docker build cache...[/dim]")
            try:
                subprocess.run(
                    ["docker", "builder", "prune", "-f"],
                    check=True,
                    capture_output=True,
                    text=True,
                )
                logger.debug("Docker build cache cleared")
            except subprocess.CalledProcessError as e:
                logger.warning(f"Could not clear Docker build cache: {e}")
                if verbose:
                    console.print(f"[dim]Warning: Could not clear build cache: {escape(str(e))}[/dim]")
            
            # Clear the cache directory
            if cache_dir:
                _clear_cache_directory(cache_dir, verbose=verbose)
        
        # Generate dynamic Spack configuration
        logger.debug("Generating dynamic Spack YAML configuration")
        spack_yaml = generate_yaml_string(
            slurm_version=version,
            gpu_support=gpu_support,
            minimal=minimal,
            additional_variants=additional_variants,
            enable_verification=verify,
        )
        logger.debug(f"Generated Spack YAML configuration ({len(spack_yaml)} chars)")

        # ========================================================================
        # STAGE 1: Build the builder image (heavily cached)
        # ========================================================================
        console.print("[bold cyan]Stage 1/2: Building Slurm with Spack...[/bold cyan]")
        
        # Generate Dockerfile with embedded spack.yaml
        logger.debug("Generating builder Dockerfile")
        dockerfile_content = get_dockerfile(spack_yaml)
        logger.debug(f"Generated Dockerfile ({len(dockerfile_content)} chars)")

        # Build builder stage only
        _build_docker_image(
            builder_image_tag,
            dockerfile_content,
            cache_dir,
            verbose=verbose,
            no_cache=no_cache,
            target="builder",  # Only build up to builder stage
        )
        
        console.print("[bold green]✓ Builder stage complete (cached for future builds)[/bold green]")

        # ========================================================================
        # STAGE 2: Build the packager image (invalidates on config changes)
        # ========================================================================
        console.print("[bold cyan]Stage 2/2: Packaging with configuration files...[/bold cyan]")
        
        # Generate packager Dockerfile that builds FROM builder
        logger.debug("Generating packager Dockerfile")
        packager_dockerfile = get_packager_dockerfile(builder_image_tag, version)
        logger.debug(f"Generated packager Dockerfile ({len(packager_dockerfile)} chars)")

        # Build packager image with config files from host
        # This will invalidate when data/slurm_assets or data/templates change
        _build_docker_image(
            packager_image_tag,
            packager_dockerfile,
            cache_dir,
            verbose=verbose,
            no_cache=False,  # Allow caching for packager stage
        )
        
        console.print("[bold green]✓ Packager stage complete[/bold green]")

        # Tag the final packager image as the main image tag for compatibility
        try:
            subprocess.run(
                ["docker", "tag", packager_image_tag, image_tag],
                check=True,
                capture_output=True,
                text=True,
            )
            logger.debug(f"Tagged {packager_image_tag} as {image_tag}")
        except subprocess.CalledProcessError as e:
            logger.warning(f"Could not tag packager image: {e}")

        # Extract the tarball from the packager image
        if cache_dir:
            console.print("[bold cyan]Extracting tarball from image...[/bold cyan]")
            extract_slurm_package_from_image(
                image_tag=packager_image_tag,
                output_dir=cache_dir,
                version=version,
                verbose=verbose,
            )

        console.print("[bold green]✓ Slurm package built successfully[/bold green]")

    except SlurmFactoryStreamExecError as e:
        msg = f"Build failed: {e}"
        logger.error(msg)
        console.print(f"[bold red]{escape(msg)}[/bold red]")
        raise SlurmFactoryError(msg)
    except Exception as e:
        msg = f"Failed to create slurm package: {e}"
        logger.error(msg)
        console.print(f"[bold red]{escape(msg)}[/bold red]")
        raise SlurmFactoryError(msg)


def extract_slurm_package_from_image(
    image_tag: str,
    output_dir: str,
    version: str,
    verbose: bool = False,
) -> None:
    """
    Extract the Slurm package tarball from a packager Docker image.

    Args:
        image_tag: Tag of the packager Docker image
        output_dir: Directory to extract the tarball to
        version: Slurm version (for finding the correct tarball)
        verbose: Whether to show detailed output

    """
    console.print(f"[bold blue]Extracting Slurm package from image {image_tag}...[/bold blue]")
    logger.debug(f"Extracting package from image {image_tag} to {output_dir}")

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    container_name = f"slurm-factory-extract-{version.replace('.', '-')}"
    tarball_name = f"slurm-{version}-software.tar.gz"
    container_tarball_path = f"/opt/slurm/build_output/{tarball_name}"

    try:
        # Create a temporary container from the image
        logger.debug(f"Creating temporary container {container_name}")
        result = subprocess.run(
            ["docker", "create", "--name", container_name, image_tag],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode != 0:
            msg = f"Failed to create container for extraction: {result.stderr}"
            logger.error(msg)
            console.print(f"[bold red]{escape(msg)}[/bold red]")
            raise SlurmFactoryError(msg)

        # Copy the tarball from the container
        logger.debug(f"Copying {container_tarball_path} from container to {output_dir}")
        console.print(f"[dim]Copying tarball to {output_dir}...[/dim]")

        result = subprocess.run(
            ["docker", "cp", f"{container_name}:{container_tarball_path}", str(output_path)],
            capture_output=True,
            text=True,
            timeout=120,
        )

        if result.returncode != 0:
            msg = f"Failed to copy tarball from container: {result.stderr}"
            logger.error(msg)
            console.print(f"[bold red]{escape(msg)}[/bold red]")
            raise SlurmFactoryError(msg)

        console.print(f"[bold green]✓ Extracted {tarball_name} to {output_dir}[/bold green]")
        logger.debug(f"Successfully extracted package to {output_dir}/{tarball_name}")

    except subprocess.TimeoutExpired:
        msg = "Extraction timed out"
        logger.error(msg)
        console.print(f"[bold red]{msg}[/bold red]")
        raise SlurmFactoryError(msg)
    except Exception as e:
        msg = f"Failed to extract package: {e}"
        logger.error(msg)
        console.print(f"[bold red]{escape(msg)}[/bold red]")
        raise SlurmFactoryError(msg)
    finally:
        # Clean up the temporary container
        try:
            subprocess.run(
                ["docker", "rm", container_name],
                capture_output=True,
                text=True,
                timeout=30,
            )
            logger.debug(f"Removed temporary container {container_name}")
        except Exception as e:
            logger.warning(f"Failed to remove temporary container: {e}")
