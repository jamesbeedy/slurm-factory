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

"""Main config module for slurm-builder."""

from dataclasses import dataclass
from pathlib import Path


@dataclass
class Settings:
    """Common settings for the entire app."""

    project_name: str

    @property
    def home_cache_dir(self) -> Path:
        """Get the ~/.slurm-factory directory."""
        return Path.home() / ".slurm-factory"

    @property
    def builds_dir(self) -> Path:
        """Get the ~/.slurm-factory/builds directory."""
        return self.home_cache_dir / "builds"

    @property
    def spack_buildcache_dir(self) -> Path:
        """Get the ~/.slurm-factory/spack-buildcache directory."""
        return self.home_cache_dir / "spack-buildcache"

    @property
    def spack_sourcecache_dir(self) -> Path:
        """Get the ~/.slurm-factory/spack-sourcecache directory."""
        return self.home_cache_dir / "spack-sourcecache"

    def ensure_cache_dirs(self) -> None:
        """
        Create all cache directories if they don't exist with proper permissions.

        These directories are mounted as Docker volumes during the build process:
        - builds_dir: Maps to CONTAINER_BUILD_OUTPUT_DIR for final build artifacts
        - spack_buildcache_dir: Maps to CONTAINER_SPACK_CACHE_DIR for binary cache
        - spack_sourcecache_dir: Maps to CONTAINER_CACHE_DIR for source tarballs

        The directories are created with 0o777 permissions to ensure Docker containers
        can read/write to them regardless of the container's user ID.
        """
        # Create directories with proper permissions (777)
        self.home_cache_dir.mkdir(mode=0o777, exist_ok=True)
        self.builds_dir.mkdir(mode=0o777, exist_ok=True)
        self.spack_buildcache_dir.mkdir(mode=0o777, exist_ok=True)
        self.spack_sourcecache_dir.mkdir(mode=0o777, exist_ok=True)
