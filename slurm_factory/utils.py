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
import site
import subprocess
import sys
from pathlib import Path

from rich.console import Console
from rich.markup import escape

from .constants import (
    BASH_HEADER,
    BUILD_TIMEOUT,
    CONTAINER_BUILD_OUTPUT_DIR,
    CONTAINER_SLURM_DIR,
    CONTAINER_SPACK_TEMPLATES_DIR,
    get_dockerfile,
    get_package_creation_script,
)
from .exceptions import SlurmFactoryError, SlurmFactoryStreamExecError
from .spack_yaml import generate_yaml_string

# Set up logging following craft-providers pattern
logger = logging.getLogger(__name__)
console = Console()


def _build_docker_image(
    image_tag: str, dockerfile_content: str, cache_dir: str, verbose: bool = False, no_cache: bool = False
) -> None:
    """
    Build a Docker image from a Dockerfile string.

    Args:
        image_tag: Tag for the Docker image
        dockerfile_content: Complete Dockerfile as a string
        cache_dir: Host directory for cache mounts
        verbose: Whether to show detailed output
        no_cache: Force a fresh build without using Docker cache

    """
    console.print(f"[bold blue]Building Docker image {image_tag}...[/bold blue]")
    logger.debug(f"Building Docker image: {image_tag}")
    logger.debug(f"Dockerfile size: {len(dockerfile_content)} characters")
    
    if no_cache:
        logger.debug("Building with --no-cache flag")
        console.print("[bold yellow]Building without cache (this may take longer)[/bold yellow]")

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


def _run_docker_container(container_name: str, image_tag: str, cache_dir: str, verbose: bool = False) -> None:
    """
    Run a Docker container from an image with cache volume mounts.

    Args:
        container_name: Name for the container
        image_tag: Image tag to run
        cache_dir: Host directory for cache mounts
        verbose: Whether to show detailed output

    """
    console.print(f"[bold blue]Starting Docker container {container_name}...[/bold blue]")
    logger.debug(f"Running Docker container: {container_name} from {image_tag}")

    try:
        # Run container in detached mode with cache mounts
        cmd = [
            "docker",
            "run",
            "-d",  # Detached mode
            "--name",
            container_name,
            # Mount cache directories
            "-v",
            f"{cache_dir}:{CONTAINER_BUILD_OUTPUT_DIR}",
            image_tag,
            "sleep",
            "infinity",  # Keep container running
        ]

        if verbose:
            logger.debug(f"Docker run command: {' '.join(cmd)}")
            console.print(f"[dim]$ {' '.join(cmd)}[/dim]")

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode != 0:
            msg = f"Failed to start Docker container: {result.stderr}"
            logger.error(msg)
            console.print(f"[bold red]{escape(msg)}[/bold red]")
            raise SlurmFactoryError(msg)

        container_id = result.stdout.strip()
        logger.debug(f"Container started with ID: {container_id}")
        console.print(f"[bold green]✓ Container {container_name} started[/bold green]")

    except subprocess.TimeoutExpired:
        msg = "Docker container start timed out"
        logger.error(msg)
        console.print(f"[bold red]{msg}[/bold red]")
        raise SlurmFactoryError(msg)
    except Exception as e:
        msg = f"Failed to start Docker container: {e}"
        logger.error(msg)
        console.print(f"[bold red]{escape(msg)}[/bold red]")
        raise SlurmFactoryError(msg)


def _exec_in_container(
    container_name: str, command: list[str], description: str, verbose: bool = False
) -> tuple[int, list[str], list[str]]:
    """
    Execute a command in a Docker container and stream output.

    Args:
        container_name: Name of the container
        command: Command to execute as list
        description: Description of the command for user
        verbose: Whether to show detailed output

    Returns:
        Tuple of (returncode, stdout_lines, stderr_lines)

    """
    logger.debug(f"Executing in container {container_name}: {' '.join(command)}")
    logger.debug(f"Description: {description}")

    console.print(f"[bold blue]{description}[/bold blue]")

    process = None
    try:
        # Build docker exec command
        cmd = ["docker", "exec", container_name] + command

        if verbose:
            logger.debug(f"Docker exec command: {' '.join(cmd)}")

        # Stream output to terminal in real-time
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,  # Merge stderr into stdout
            text=True,
            bufsize=1,  # Line buffered
        )

        stdout_lines: list[str] = []

        # Stream output line by line
        if process.stdout:
            for line in process.stdout:
                line = line.rstrip()
                if line:
                    stdout_lines.append(line)
                    # Always show output for build commands
                    console.print(f"  {escape(line)}")
                    logger.debug(f"Container exec: {line}")

        # Wait for process to complete
        returncode = process.wait(timeout=BUILD_TIMEOUT)

        if returncode != 0:
            msg = f"Command failed with exit code {returncode}"
            logger.error(msg)
            logger.error(f"Command was: {' '.join(command)}")
            console.print(f"[bold red]{msg}[/bold red]")
            # Show last 20 lines of output on failure
            console.print("[bold red]Last lines of output:[/bold red]")
            last_lines = stdout_lines[-20:] if len(stdout_lines) > 20 else stdout_lines
            for line in last_lines:
                if line.strip():
                    console.print(f"[red]  {escape(line)}[/red]")
            raise SlurmFactoryStreamExecError(msg)

        logger.debug("Command completed successfully")
        stderr_lines: list[str] = []
        return (returncode, stdout_lines, stderr_lines)

    except subprocess.TimeoutExpired:
        msg = f"Command execution timed out after {BUILD_TIMEOUT} seconds"
        logger.error(msg)
        console.print(f"[bold red]{msg}[/bold red]")
        if process:
            process.kill()
        raise SlurmFactoryStreamExecError(msg)
    except Exception as e:
        msg = f"Command execution failed: {e}"
        logger.error(msg)
        console.print(f"[bold red]{escape(msg)}[/bold red]")
        raise SlurmFactoryStreamExecError(msg)


def _copy_from_container(container_name: str, source_path: str, dest_path: str) -> None:
    """
    Copy files from a Docker container to the host.

    Args:
        container_name: Name of the container
        source_path: Path inside the container
        dest_path: Destination path on the host

    """
    logger.debug(f"Copying from container {container_name}:{source_path} to {dest_path}")

    try:
        cmd = ["docker", "cp", f"{container_name}:{source_path}", dest_path]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,
        )

        if result.returncode != 0:
            msg = f"Failed to copy from container: {result.stderr}"
            logger.error(msg)
            raise SlurmFactoryError(msg)

        logger.debug(f"Successfully copied {source_path} from container")

    except subprocess.TimeoutExpired:
        msg = "Copy from container timed out"
        logger.error(msg)
        raise SlurmFactoryError(msg)
    except Exception as e:
        msg = f"Failed to copy from container: {e}"
        logger.error(msg)
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


def _stop_and_remove_container(container_name: str, verbose: bool = False) -> None:
    """
    Stop and remove a Docker container.

    Args:
        container_name: Name of the container
        verbose: Whether to show detailed output

    """
    logger.debug(f"Stopping and removing container: {container_name}")

    try:
        # Stop container
        subprocess.run(
            ["docker", "stop", container_name],
            capture_output=True,
            text=True,
            timeout=30,
        )

        # Remove container
        subprocess.run(
            ["docker", "rm", container_name],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if verbose:
            console.print(f"[dim]Removed container {container_name}[/dim]")
        logger.debug(f"Container {container_name} stopped and removed")

    except Exception as e:
        logger.warning(f"Failed to clean up container {container_name}: {e}")
        # Don't raise - cleanup is best-effort


def _copy_templates_to_container(container_name: str, verbose: bool = False) -> None:
    """Copy template files into the container."""
    templates_source = _get_data_file("templates")

    if not templates_source.exists():
        logger.warning(f"Templates directory not found at {templates_source}")
        return

    logger.debug(f"Copying template files from {templates_source} into container {container_name}")

    # Create the templates directory in the container first
    _exec_in_container(
        container_name,
        ["mkdir", "-p", CONTAINER_SPACK_TEMPLATES_DIR],
        "Creating templates directory in container",
        verbose=verbose,
    )

    # Copy each template file into the container
    for template_file in templates_source.glob("*"):
        if template_file.is_file():
            destination_path = f"{CONTAINER_SPACK_TEMPLATES_DIR}/{template_file.name}"

            # Use docker cp to copy files
            try:
                cmd = ["docker", "cp", str(template_file), f"{container_name}:{destination_path}"]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

                if result.returncode != 0:
                    logger.error(f"Failed to copy template file {template_file.name}: {result.stderr}")
                    raise SlurmFactoryError(f"Failed to copy template: {template_file.name}")

                logger.info(f"Copied {template_file.name} to container at {CONTAINER_SPACK_TEMPLATES_DIR}")
            except Exception as e:
                logger.error(f"Failed to copy template file {template_file.name}: {e}")
                raise

    logger.debug("Copied template files to container")


def _copy_slurm_assets_to_container(container_name: str, verbose: bool = False) -> None:
    """Copy slurm_assets files into the container."""
    slurm_assets_source = _get_data_file("slurm_assets")

    if not slurm_assets_source.exists():
        logger.warning(f"Slurm assets directory not found at {slurm_assets_source}")
        return

    logger.debug(f"Copying slurm_assets files from {slurm_assets_source} into container {container_name}")

    # Create the slurm_assets directory in the container first
    container_assets_dir = f"{CONTAINER_SLURM_DIR}/slurm_assets"
    _exec_in_container(
        container_name,
        ["mkdir", "-p", container_assets_dir],
        "Creating slurm_assets directory in container",
        verbose=verbose,
    )

    # Copy the entire slurm_assets directory structure into the container
    try:
        cmd = [
            "docker",
            "cp",
            str(slurm_assets_source) + "/.",
            f"{container_name}:{container_assets_dir}/",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

        if result.returncode != 0:
            logger.error(f"Failed to copy slurm_assets: {result.stderr}")
            raise SlurmFactoryError("Failed to copy slurm_assets directory")

        if verbose:
            console.print("[dim]Copied slurm_assets to container[/dim]")

    except subprocess.TimeoutExpired:
        msg = "Copying slurm_assets timed out"
        logger.error(msg)
        raise SlurmFactoryError(msg)
    except Exception as e:
        if not isinstance(e, SlurmFactoryError):
            logger.error(f"Failed to copy slurm_assets: {e}")
            raise

    logger.debug("Copied slurm_assets files to container")


def _get_data_file(filename: str) -> Path:
    """Get path to a data file, prioritizing installed package locations over development."""
    # First priority: Virtual environment (for pip installed packages)
    if hasattr(sys, "prefix") and sys.prefix != sys.base_prefix:
        # We're in a virtual environment
        venv_path = Path(sys.prefix) / "share" / "slurm-factory" / filename
        if venv_path.exists():
            return venv_path.resolve()

    # Second priority: System-wide installation locations
    try:
        # Check each site-packages directory for shared data
        for site_dir in site.getsitepackages() + [site.getusersitepackages()]:
            if site_dir:
                installed_path = Path(site_dir) / "share" / "slurm-factory" / filename
                if installed_path.exists():
                    return installed_path.resolve()

                # Also check the parent directory of site-packages for share
                parent_share = Path(site_dir).parent / "share" / "slurm-factory" / filename
                if parent_share.exists():
                    return parent_share.resolve()
    except Exception:
        pass

    # Last fallback: Development mode (files in current directory)
    dev_path = Path.cwd() / "data" / filename
    if dev_path.exists():
        return dev_path.resolve()

    # If nothing found, return the development path anyway (will cause an error if file doesn't exist)
    raise FileNotFoundError(f"Data file '{filename}' not found in any expected location")


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
    """Create slurm package in a Docker container."""
    console.print("[bold blue]Creating slurm package in Docker container...[/bold blue]")

    logger.debug(
        f"Building Slurm package: version={version}, gpu={gpu_support}, minimal={minimal}, verify={verify}, no_cache={no_cache}"
    )

    try:
        # If no_cache is enabled, clean up everything first
        if no_cache:
            console.print("[bold yellow]🗑️  Performing fresh build - cleaning all caches...[/bold yellow]")
            
            # Remove old Docker image
            _remove_old_docker_image(image_tag, verbose=verbose)
            
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

        # Generate Dockerfile with embedded spack.yaml
        logger.debug("Generating Dockerfile")
        dockerfile_content = get_dockerfile(spack_yaml)
        logger.debug(f"Generated Dockerfile ({len(dockerfile_content)} chars)")

        # Build Docker image
        _build_docker_image(image_tag, dockerfile_content, cache_dir, verbose=verbose, no_cache=no_cache)

        # Run container
        _run_docker_container(container_name, image_tag, cache_dir, verbose=verbose)

        # Copy templates into container
        logger.debug("Copying Lmod module templates to container...")
        _copy_templates_to_container(container_name, verbose=verbose)

        # Copy slurm_assets into container
        logger.debug("Copying slurm_assets to container...")
        _copy_slurm_assets_to_container(container_name, verbose=verbose)

        # Execute package creation script
        exec_script = get_package_creation_script(version=version)
        logger.debug(f"Executing package creation script ({len(exec_script)} chars)")

        _exec_in_container(
            container_name,
            BASH_HEADER + [exec_script],
            f"Building Slurm {version} package",
            verbose=verbose,
        )
        logger.debug("Successfully completed package creation script")

        console.print("[bold green]✓ Slurm package built successfully[/bold green]")

        # Cleanup container (but keep image for potential reuse)
        _stop_and_remove_container(container_name, verbose=verbose)

    except SlurmFactoryStreamExecError as e:
        msg = f"Build failed: {e}"
        logger.error(msg)
        console.print(f"[bold red]{escape(msg)}[/bold red]")
        # Leave container running for debugging
        console.print(f"[yellow]Container {container_name} left running for debugging[/yellow]")
        console.print(f"[yellow]Connect with: docker exec -it {container_name} bash[/yellow]")
        raise SlurmFactoryError(msg)
    except Exception as e:
        msg = f"Failed to create slurm package: {e}"
        logger.error(msg)
        console.print(f"[bold red]{escape(msg)}[/bold red]")
        # Cleanup on unexpected errors
        _stop_and_remove_container(container_name, verbose=verbose)
        raise SlurmFactoryError(msg)
