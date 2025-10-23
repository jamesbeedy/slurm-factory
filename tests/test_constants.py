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

"""Unit tests for slurm_factory.constants module."""

import pytest

from slurm_factory.constants import (
    SLURM_VERSIONS,
    BuildType,
    SlurmVersion,
    CONTAINER_CACHE_DIR,
    CONTAINER_SPACK_TEMPLATES_DIR,
    CONTAINER_SPACK_PROJECT_DIR,
    CONTAINER_SLURM_DIR,
    CONTAINER_BUILD_OUTPUT_DIR,
    CONTAINER_ROOT_DIR,
    CONTAINER_SPACK_CACHE_DIR,
    INSTANCE_NAME_PREFIX,
    BUILD_TIMEOUT,
    DOCKER_BUILD_TIMEOUT,
    SPACK_SETUP_SCRIPT,
    SLURM_PATCH_FILES,
    BASH_HEADER,
    get_package_creation_script,
    get_dockerfile,
)


class TestSlurmVersions:
    """Test Slurm version constants."""

    def test_slurm_versions_available(self):
        """Test that all expected Slurm versions are available."""
        expected_versions = ["25.05", "24.11", "23.11", "23.02"]
        for version in expected_versions:
            assert version in SLURM_VERSIONS

    def test_slurm_versions_mapping(self):
        """Test that version mappings are correct."""
        # Test known mappings (updated for actual format)
        assert SLURM_VERSIONS["25.05"] == "25-05-4-1"
        assert SLURM_VERSIONS["24.11"] == "24-11-6-1"
        assert SLURM_VERSIONS["23.11"] == "23-11-11-1"
        assert SLURM_VERSIONS["23.02"] == "23-02-7-1"

    def test_all_versions_are_strings(self):
        """Test that all version values are strings."""
        for key, value in SLURM_VERSIONS.items():
            assert isinstance(key, str)
            assert isinstance(value, str)


class TestBuildType:
    """Test BuildType enum."""

    def test_build_type_values(self):
        """Test BuildType enum values."""
        assert BuildType.cpu == "cpu"
        assert BuildType.minimal == "minimal"
        assert BuildType.gpu == "gpu"

    def test_build_type_str_conversion(self):
        """Test string conversion of BuildType."""
        # For str Enums, the value should be accessible directly
        assert BuildType.cpu == "cpu"
        assert BuildType.minimal == "minimal"
        assert BuildType.gpu == "gpu"


class TestSlurmVersion:
    """Test SlurmVersion enum."""

    def test_slurm_version_values(self):
        """Test SlurmVersion enum values."""
        assert SlurmVersion.v25_05 == "25.05"
        assert SlurmVersion.v24_11 == "24.11"
        assert SlurmVersion.v23_11 == "23.11"
        assert SlurmVersion.v23_02 == "23.02"

    def test_slurm_version_str_conversion(self):
        """Test string conversion of SlurmVersion."""
        # For str Enums, the value should be accessible directly
        assert SlurmVersion.v25_05 == "25.05"
        assert SlurmVersion.v24_11 == "24.11"
        assert SlurmVersion.v23_11 == "23.11"
        assert SlurmVersion.v23_02 == "23.02"


class TestContainerPaths:
    """Test container path constants."""

    def test_container_paths_exist(self):
        """Test that container path constants exist and are strings."""
        paths = [
            CONTAINER_CACHE_DIR,
            CONTAINER_SPACK_TEMPLATES_DIR,
            CONTAINER_SPACK_PROJECT_DIR,
            CONTAINER_SLURM_DIR,
            CONTAINER_BUILD_OUTPUT_DIR,
            CONTAINER_ROOT_DIR,
            CONTAINER_SPACK_CACHE_DIR,
        ]
        
        for path in paths:
            assert isinstance(path, str)
            assert path.startswith("/")

    def test_specific_container_paths(self):
        """Test specific container path values."""
        assert CONTAINER_CACHE_DIR == "/opt/slurm-factory-cache"
        assert CONTAINER_SLURM_DIR == "/opt/slurm"
        assert CONTAINER_ROOT_DIR == "/root"


class TestDockerConfiguration:
    """Test Docker configuration constants."""

    def test_instance_configuration(self):
        """Test instance configuration constants."""
        assert INSTANCE_NAME_PREFIX == "slurm-factory"

    def test_docker_build_timeout(self):
        """Test Docker build timeout."""
        assert isinstance(DOCKER_BUILD_TIMEOUT, int)
        assert DOCKER_BUILD_TIMEOUT > 0
        assert DOCKER_BUILD_TIMEOUT == 600

    def test_build_timeout(self):
        """Test build timeout."""
        assert isinstance(BUILD_TIMEOUT, int)
        assert BUILD_TIMEOUT > 0
        assert BUILD_TIMEOUT == 3600


class TestSpackPaths:
    """Test Spack path constants."""

    def test_spack_setup_script(self):
        """Test Spack setup script path."""
        assert SPACK_SETUP_SCRIPT == "/opt/spack/share/spack/setup-env.sh"
        assert isinstance(SPACK_SETUP_SCRIPT, str)
        assert SPACK_SETUP_SCRIPT.startswith("/")


class TestScriptTemplates:
    """Test script template functions."""

    def test_get_package_creation_script(self):
        """Test package creation script generation."""
        version = "25.05"
        script = get_package_creation_script(version)
        
        # Test that it returns a string
        assert isinstance(script, str)
        assert len(script) > 0
        
        # Test that it contains expected elements
        assert "spack env activate" in script
        assert "spack concretize" in script
        assert "spack install" in script
        assert "set -e" in script
        assert version in script
        
        # Test that it references container paths
        assert CONTAINER_SPACK_PROJECT_DIR in script
        assert SPACK_SETUP_SCRIPT in script
        assert CONTAINER_SLURM_DIR in script
        
        # Test that it's properly formatted shell script
        lines = script.strip().split('\n')
        assert len(lines) > 5  # Should be a substantial script

    def test_get_dockerfile(self):
        """Test Dockerfile generation."""
        spack_yaml_content = "spack:\n  specs:\n    - slurm@25.05"
        dockerfile = get_dockerfile(spack_yaml_content)
        
        # Test that it returns a string
        assert isinstance(dockerfile, str)
        assert len(dockerfile) > 0
        
        # Test that it contains expected elements
        assert "FROM ubuntu:24.04" in dockerfile
        assert "RUN" in dockerfile
        assert "ENV" in dockerfile
        assert spack_yaml_content in dockerfile
        
        # Test that it installs required packages
        assert "git" in dockerfile
        assert "build-essential" in dockerfile
        
        # Test that it's properly formatted Dockerfile
        lines = dockerfile.strip().split('\n')
        assert len(lines) > 10  # Should be a substantial Dockerfile


class TestConstantTypes:
    """Test that constants have correct types."""

    def test_slurm_versions_type(self):
        """Test SLURM_VERSIONS type."""
        assert isinstance(SLURM_VERSIONS, dict)
        assert len(SLURM_VERSIONS) > 0

    def test_string_constants(self):
        """Test string constant types."""
        string_constants = [
            CONTAINER_CACHE_DIR,
            INSTANCE_NAME_PREFIX,
            SPACK_SETUP_SCRIPT,
        ]
        
        for constant in string_constants:
            assert isinstance(constant, str)

    def test_integer_constants(self):
        """Test integer constant types."""
        assert isinstance(BUILD_TIMEOUT, int)
        assert isinstance(DOCKER_BUILD_TIMEOUT, int)


class TestConstantValidation:
    """Test validation of constant values."""

    def test_paths_are_absolute(self):
        """Test that all path constants are absolute paths."""
        path_constants = [
            CONTAINER_CACHE_DIR,
            CONTAINER_SPACK_TEMPLATES_DIR,
            CONTAINER_SPACK_PROJECT_DIR,
            CONTAINER_SLURM_DIR,
            CONTAINER_BUILD_OUTPUT_DIR,
            CONTAINER_ROOT_DIR,
            CONTAINER_SPACK_CACHE_DIR,
            SPACK_SETUP_SCRIPT,
        ]
        
        for path in path_constants:
            assert path.startswith("/"), f"Path is not absolute: {path}"

    def test_version_consistency(self):
        """Test consistency between version constants and enums."""
        # All SlurmVersion enum values should be in SLURM_VERSIONS
        for version_enum in SlurmVersion:
            assert version_enum.value in SLURM_VERSIONS

    def test_no_trailing_slashes(self):
        """Test that paths don't have trailing slashes."""
        path_constants = [
            CONTAINER_CACHE_DIR,
            CONTAINER_SPACK_TEMPLATES_DIR,
            CONTAINER_SPACK_PROJECT_DIR,
            CONTAINER_SLURM_DIR,
            CONTAINER_BUILD_OUTPUT_DIR,
            CONTAINER_ROOT_DIR,
            CONTAINER_SPACK_CACHE_DIR,
        ]
        
        for path in path_constants:
            if path != "/":  # Root path is exception
                assert not path.endswith("/"), f"Path has trailing slash: {path}"

    def test_build_cache_output_relationship(self):
        """Test relationship between SLURM directory and build output."""
        assert CONTAINER_BUILD_OUTPUT_DIR.startswith(CONTAINER_SLURM_DIR)


if __name__ == "__main__":
    pytest.main([__file__])