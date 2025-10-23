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

"""Unit tests for slurm_factory.spack_yaml module."""

import pytest
import yaml

from slurm_factory.constants import SLURM_VERSIONS
from slurm_factory.spack_yaml import (
    cpu_only_config,
    generate_module_config,
    generate_spack_config,
    generate_yaml_string,
    get_comment_header,
    gpu_enabled_config,
    minimal_config,
    verification_config,
)


class TestSpackConfigGeneration:
    """Test Spack configuration generation."""

    def test_generate_spack_config_default(self):
        """Test default Spack configuration generation."""
        config = generate_spack_config()
        
        # Test top-level structure
        assert "spack" in config
        spack_config = config["spack"]
        
        # Test required sections
        required_sections = ["specs", "concretizer", "view", "config", "mirrors", "compilers", "packages", "modules"]
        for section in required_sections:
            assert section in spack_config, f"Missing section: {section}"
        
        # Test default specs
        assert isinstance(spack_config["specs"], list)
        assert len(spack_config["specs"]) > 0
        
        # Test that all specs have compiler constraints
        for spec in spack_config["specs"]:
            assert "%gcc@13.3.0" in spec, f"Spec missing compiler constraint: {spec}"

    def test_generate_spack_config_versions(self):
        """Test configuration generation for all supported Slurm versions."""
        for version in SLURM_VERSIONS.keys():
            config = generate_spack_config(slurm_version=version)
            assert "spack" in config
            
            # Check that the slurm package version is correct
            slurm_specs = [spec for spec in config["spack"]["specs"] if "slurm_factory.slurm@" in spec]
            assert len(slurm_specs) > 0, f"No slurm spec found for version {version}"
            
            expected_package_version = SLURM_VERSIONS[version]
            slurm_spec = slurm_specs[0]
            assert expected_package_version in slurm_spec, f"Incorrect package version in {slurm_spec}"

    def test_generate_spack_config_gpu_support(self):
        """Test GPU support configuration."""
        # CPU-only config
        cpu_config = generate_spack_config(gpu_support=False)
        slurm_specs = [spec for spec in cpu_config["spack"]["specs"] if "slurm_factory.slurm@" in spec]
        slurm_spec = slurm_specs[0]
        assert "~nvml" in slurm_spec
        assert "~rsmi" in slurm_spec
        
        # GPU-enabled config
        gpu_config = generate_spack_config(gpu_support=True)
        slurm_specs = [spec for spec in gpu_config["spack"]["specs"] if "slurm_factory.slurm@" in spec]
        slurm_spec = slurm_specs[0]
        assert "+nvml" in slurm_spec
        assert "+rsmi" in slurm_spec
        
        # Check view configuration uses runtime dependencies
        assert gpu_config["spack"]["view"]["default"]["link"] == "run"

    def test_generate_spack_config_minimal(self):
        """Test minimal configuration."""
        minimal_config_data = generate_spack_config(minimal=True)
        
        # Check that minimal build excludes OpenMPI and some features
        slurm_specs = [spec for spec in minimal_config_data["spack"]["specs"] if "slurm_factory.slurm@" in spec]
        slurm_spec = slurm_specs[0]
        assert "~hwloc" in slurm_spec
        assert "~pmix" in slurm_spec
        assert "~restd" in slurm_spec
        
        # Check that OpenMPI is not in specs for minimal build
        openmpi_specs = [spec for spec in minimal_config_data["spack"]["specs"] if spec.startswith("openmpi@")]
        assert len(openmpi_specs) == 0

    def test_compiler_configuration(self):
        """Test compiler configuration."""
        config = generate_spack_config()
        compilers = config["spack"]["compilers"]
        
        assert len(compilers) == 1
        compiler = compilers[0]["compiler"]
        
        # Test compiler spec and paths
        assert compiler["spec"] == "gcc@=13.3.0"
        assert compiler["paths"]["cc"] == "/usr/bin/gcc"
        assert compiler["paths"]["cxx"] == "/usr/bin/g++"
        assert compiler["paths"]["f77"] == "/usr/bin/gfortran"
        assert compiler["paths"]["fc"] == "/usr/bin/gfortran"
        
        # Test RPATH configuration (empty by default, can be customized later)
        assert "extra_rpaths" in compiler
        rpaths = compiler["extra_rpaths"]
        assert isinstance(rpaths, list)

    def test_gcc_external_prevention(self):
        """Test that GCC external package is properly configured."""
        config = generate_spack_config()
        packages = config["spack"]["packages"]
        
        # Test that GCC is configured to prevent external detection
        assert "gcc" in packages
        gcc_config = packages["gcc"]
        assert gcc_config["buildable"] is False
        assert "externals" in gcc_config
        # Should have one external entry for the system GCC
        assert len(gcc_config["externals"]) == 1
        external = gcc_config["externals"][0]
        assert "gcc@13.3.0" in external["spec"]
        assert external["prefix"] == "/usr"

    def test_package_configurations(self):
        """Test package-specific configurations."""
        config = generate_spack_config()
        packages = config["spack"]["packages"]
        
        # Test external build tools
        external_tools = ["cmake", "python", "autoconf", "automake", "libtool"]
        for tool in external_tools:
            assert tool in packages
            assert packages[tool]["buildable"] is False
            assert "externals" in packages[tool]
        
        # Test runtime libraries are buildable
        runtime_libs = ["munge", "json-c", "curl", "openssl", "readline", "ncurses"]
        for lib in runtime_libs:
            assert lib in packages
            assert packages[lib]["buildable"] is True
        
        # Test libjwt configuration
        assert "libjwt" in packages
        libjwt_config = packages["libjwt"]
        assert libjwt_config["buildable"] is True
        assert "require" in libjwt_config
        requirements = libjwt_config["require"]
        assert "^openssl@3:" in requirements
        assert "^jansson" in requirements


class TestModuleConfiguration:
    """Test module configuration generation."""

    def test_generate_module_config_default(self):
        """Test default module configuration."""
        module_config = generate_module_config()
        
        # Test structure
        assert "default" in module_config
        default_config = module_config["default"]
        assert "enable" in default_config
        assert "lmod" in default_config
        
        # Test Lmod configuration
        lmod_config = default_config["lmod"]
        assert "core_compilers" in lmod_config
        assert "gcc@13.3.0" in lmod_config["core_compilers"]
        assert lmod_config["hierarchy"] == []
        
        # Test included modules
        assert "slurm" in lmod_config["include"]
        assert "openmpi" in lmod_config["include"]

    def test_generate_module_config_minimal(self):
        """Test minimal module configuration."""
        module_config = generate_module_config(minimal=True)
        lmod_config = module_config["default"]["lmod"]
        
        # Minimal build should only include slurm
        assert lmod_config["include"] == ["slurm"]

    def test_slurm_module_configuration(self):
        """Test Slurm-specific module configuration."""
        module_config = generate_module_config()
        slurm_config = module_config["default"]["lmod"]["slurm"]
        
        # Test environment variables
        env_vars = slurm_config["environment"]["set"]
        assert "SLURM_CONF" in env_vars
        assert "SLURM_ROOT" in env_vars
        assert "SLURM_BUILD_TYPE" in env_vars
        assert "SLURM_VERSION" in env_vars
        assert "SLURM_PREFIX" in env_vars
        assert "SLURM_MODULE_HELP" in env_vars
        assert "SLURM_COMPILER" in env_vars
        assert "SLURM_TARGET_ARCH" in env_vars
        assert "SLURM_GCC_RUNTIME_PREFIX" in env_vars
        
        # Test path modifications
        paths = slurm_config["environment"]["prepend_path"]
        assert "PATH" in paths
        assert "CPATH" in paths
        assert "PKG_CONFIG_PATH" in paths
        assert "MANPATH" in paths
        assert "CMAKE_PREFIX_PATH" in paths


class TestConvenienceFunctions:
    """Test convenience configuration functions."""

    def test_cpu_only_config(self):
        """Test CPU-only convenience function."""
        config = cpu_only_config()
        assert "spack" in config
        
        # Should be equivalent to generate_spack_config with defaults
        default_config = generate_spack_config()
        assert config == default_config

    def test_gpu_enabled_config(self):
        """Test GPU-enabled convenience function."""
        config = gpu_enabled_config()
        assert "spack" in config
        
        # Should have GPU support enabled
        slurm_specs = [spec for spec in config["spack"]["specs"] if "slurm_factory.slurm@" in spec]
        slurm_spec = slurm_specs[0]
        assert "+nvml" in slurm_spec
        assert "+rsmi" in slurm_spec

    def test_minimal_config(self):
        """Test minimal convenience function."""
        config = minimal_config()
        assert "spack" in config
        
        # Should be minimal build
        slurm_specs = [spec for spec in config["spack"]["specs"] if "slurm_factory.slurm@" in spec]
        slurm_spec = slurm_specs[0]
        assert "~hwloc" in slurm_spec

    def test_verification_config(self):
        """Test verification convenience function."""
        config = verification_config()
        assert "spack" in config
        
        # Should have verification enabled
        assert "verify" in config["spack"]["config"]
        verify_config = config["spack"]["config"]["verify"]
        assert verify_config["relocatable"] is True
        assert verify_config["dependencies"] is True
        assert verify_config["shared_libraries"] is True


class TestYAMLGeneration:
    """Test YAML string generation."""

    def test_generate_yaml_string(self):
        """Test YAML string generation."""
        yaml_string = generate_yaml_string()
        
        # Test that it's a valid YAML string
        assert isinstance(yaml_string, str)
        assert len(yaml_string) > 0
        
        # Test that it can be parsed as YAML
        parsed = yaml.safe_load(yaml_string)
        assert "spack" in parsed
        
        # Test that it has a comment header
        lines = yaml_string.split('\n')
        assert lines[0].startswith("#")

    def test_generate_yaml_string_versions(self):
        """Test YAML generation for different versions."""
        for version in SLURM_VERSIONS.keys():
            yaml_string = generate_yaml_string(slurm_version=version)
            
            # Should be valid YAML
            parsed = yaml.safe_load(yaml_string)
            assert "spack" in parsed
            
            # Should contain the correct version in comment
            assert version in yaml_string

    def test_get_comment_header(self):
        """Test comment header generation."""
        # Test different configurations
        header = get_comment_header("25.05", False, False)
        assert "25.05" in header
        assert "(optimized for minimal runtime footprint)" in header
        
        header = get_comment_header("25.05", True, False)
        assert "25.05" in header
        assert "with GPU support" in header
        
        header = get_comment_header("25.05", False, True)
        assert "25.05" in header
        assert "(minimal build - basic Slurm only)" in header


class TestConfigurationValidation:
    """Test configuration validation and consistency."""

    def test_view_packages_consistency(self):
        """Test that view configuration uses runtime dependencies."""
        # Standard build
        config = generate_spack_config()
        view_config = config["spack"]["view"]["default"]
        
        # Should use runtime dependency linking
        assert view_config["link"] == "run"
        assert view_config["link_type"] == "hardlink"
        
        # Should exclude build tools (with ^ prefix for Spack spec matching)
        assert "^cmake" in view_config["exclude"]
        assert "^autoconf" in view_config["exclude"]

    def test_minimal_view_packages(self):
        """Test view configuration for minimal build."""
        config = generate_spack_config(minimal=True)
        view_config = config["spack"]["view"]["default"]
        
        # Should still use runtime dependency linking
        assert view_config["link"] == "run"
        
        # Build tools should still be excluded
        assert "^cmake" in view_config["exclude"]

    def test_gpu_view_packages(self):
        """Test view configuration for GPU build."""
        config = generate_spack_config(gpu_support=True)
        view_config = config["spack"]["view"]["default"]
        
        # Should use runtime dependency linking (GPU libs will be included automatically)
        assert view_config["link"] == "run"

    def test_concretizer_settings(self):
        """Test concretizer configuration."""
        config = generate_spack_config()
        concretizer = config["spack"]["concretizer"]
        
        assert concretizer["unify"] is True
        assert concretizer["reuse"] is False  # Build from source, don't reuse

    def test_mirror_configuration(self):
        """Test mirror configuration."""
        config = generate_spack_config()
        mirrors = config["spack"]["mirrors"]
        
        # Should have spack-public mirror for source downloads
        assert "spack-public" in mirrors
        
        # Test mirror properties
        assert mirrors["spack-public"]["url"] == "https://mirror.spack.io"
        assert mirrors["spack-public"]["signed"] is False


class TestParameterValidation:
    """Test parameter validation."""

    def test_invalid_slurm_version(self):
        """Test invalid Slurm version handling."""
        with pytest.raises(ValueError) as exc_info:
            generate_spack_config(slurm_version="99.99")
        assert "Unsupported Slurm version" in str(exc_info.value)

    def test_valid_parameters(self):
        """Test valid parameter combinations."""
        # All valid combinations should work without errors
        for version in SLURM_VERSIONS.keys():
            for gpu in [True, False]:
                for minimal in [True, False]:
                    for verify in [True, False]:
                        config = generate_spack_config(
                            slurm_version=version,
                            gpu_support=gpu,
                            minimal=minimal,
                            enable_verification=verify
                        )
                        assert "spack" in config


if __name__ == "__main__":
    pytest.main([__file__])
