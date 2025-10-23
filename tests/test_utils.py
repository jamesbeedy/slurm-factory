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

"""Unit tests for slurm_factory.utils module."""

import pytest


# Note: get_base_instance_name function was removed from utils.py
# The related tests have been removed


class TestConstants:
    """Test constants and imports from utils module."""

    def test_logging_setup(self):
        """Test that logging is properly configured."""
        from slurm_factory import utils
        
        # Should have logger and console defined
        assert hasattr(utils, 'logger')
        assert hasattr(utils, 'console')

    def test_exception_imports(self):
        """Test that custom exceptions can be accessed."""
        from slurm_factory import exceptions
        
        # Should be able to access exception classes from exceptions module
        assert hasattr(exceptions, 'SlurmFactoryError')
        assert hasattr(exceptions, 'SlurmFactoryInstanceCreationError')
        assert hasattr(exceptions, 'SlurmFactoryStreamExecError')


class TestModuleStructure:
    """Test the overall structure of the utils module."""

    def test_module_docstring(self):
        """Test that module has appropriate docstring."""
        from slurm_factory import utils
        
        assert utils.__doc__ is not None
        assert len(utils.__doc__.strip()) > 0

    def test_required_functions_exist(self):
        """Test that expected functions exist in the module."""
        from slurm_factory import utils
        
        # Test for existence of key functions
        expected_functions = [
            'create_slurm_package',
            'extract_slurm_package_from_image',
            '_build_docker_image',
            '_remove_old_docker_image',
            '_clear_cache_directory',
        ]
        
        for func_name in expected_functions:
            assert hasattr(utils, func_name)
            assert callable(getattr(utils, func_name))

    def test_module_imports(self):
        """Test that the module imports are working."""
        # This test ensures the module can be imported without errors
        try:
            from slurm_factory import utils
            assert utils is not None
        except ImportError as e:
            pytest.fail(f"Failed to import utils module: {e}")


if __name__ == "__main__":
    pytest.main([__file__])
