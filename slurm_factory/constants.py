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

"""Constants of slurm-factory."""

import textwrap
from enum import Enum
from pathlib import Path

# Mapping of user-facing version strings to Spack package versions
SLURM_VERSIONS = {
    "25.05": "25-05-4-1",
    "24.11": "24-11-6-1",
    "23.11": "23-11-11-1",
    "23.02": "23-02-7-1",
}


class SlurmVersion(str, Enum):
    """Available Slurm versions for building."""

    v25_05 = "25.05"
    v24_11 = "24.11"
    v23_11 = "23.11"
    v23_02 = "23.02"


class BuildType(str, Enum):
    """Build type options for Slurm."""

    cpu = "cpu"
    gpu = "gpu"
    minimal = "minimal"


# Docker configuration
INSTANCE_NAME_PREFIX = "slurm-factory"

# Timeouts (in seconds)
BUILD_TIMEOUT = 3600  # 1 hour for full build
DOCKER_BUILD_TIMEOUT = 600  # 10 minutes for image build

# Spack repository paths
SPACK_SETUP_SCRIPT = "/opt/spack/share/spack/setup-env.sh"

# Container paths
CONTAINER_CACHE_DIR = "/opt/slurm-factory-cache"
CONTAINER_SPACK_TEMPLATES_DIR = "/opt/spack/share/spack/templates"
CONTAINER_SPACK_PROJECT_DIR = "/root/spack-project"
CONTAINER_SLURM_DIR = "/opt/slurm"
CONTAINER_BUILD_OUTPUT_DIR = f"{CONTAINER_SLURM_DIR}/build_output"
CONTAINER_ROOT_DIR = "/root"
CONTAINER_SPACK_CACHE_DIR = "/root/.cache/spack"

# Patch files
SLURM_PATCH_FILES = ["slurm_prefix.patch", "package.py"]

# Shell script templates
BASH_HEADER = ["bash", "-c"]


def get_module_template_content() -> str:
    """Return the embedded Lmod module template content."""
    template_path = Path(__file__).parent.parent / "data" / "templates" / "relocatable_modulefile.lua"
    return template_path.read_text()


def get_modulerc_creation_script(module_dir: str, modulerc_path: str) -> str:
    """
    Generate bash script to create the .modulerc.lua file.

    Args:
        module_dir: Directory containing the .lua module files
        modulerc_path: Full path where .modulerc.lua should be created

    Returns:
        Single-line bash script as a string

    """
    # Use printf with %s for proper escaping, avoiding single quotes in echo
    # This avoids issues when embedded in complex shell scripts
    return (
        f'MODULE_LUA_FILE=$(ls {module_dir}/*.lua | head -1) && '
        f'[ -n "$MODULE_LUA_FILE" ] && '
        f'MODULE_VERSION=$(basename "$MODULE_LUA_FILE" .lua) && '
        f'printf "module_version(\\"%s\\",\\"default\\")\\n" "$MODULE_VERSION" > {modulerc_path}'
    )


def get_install_system_deps_script() -> str:
    """Generate script to install system dependencies for Spack."""
    return textwrap.dedent("""\
        apt-get update && apt-get upgrade -y && \\
        apt-get install -y \\
        git \\
        build-essential \\
        python3 \\
        unzip \\
        gfortran \\
        autoconf \\
        automake \\
        libtool \\
        bison \\
        flex \\
        cmake \\
        make \\
        m4 \\
        pkg-config \\
        ccache \\
        findutils \\
        diffutils \\
        tar \\
        gawk \\
        gettext \\
        lmod \\
        ca-certificates \\
        wget && \\
        apt-get clean && rm -rf /var/lib/apt/lists/*
    """).strip()


def get_install_spack_script() -> str:
    """Generate script to install Spack."""
    return textwrap.dedent(
        """\
        git clone --depth 1 --branch v1.0.0 https://github.com/spack/spack.git /opt/spack && \\
        chown -R root:root /opt/spack && chmod -R a+rX /opt/spack
    """
    ).strip()


def get_spack_profile_script() -> str:
    """Generate script to set up Spack profile."""
    return textwrap.dedent("""\
        echo 'source /opt/spack/share/spack/setup-env.sh' >> /etc/profile.d/spack.sh && \\
        chmod 644 /etc/profile.d/spack.sh
    """).strip()


def get_create_directories_script() -> str:
    """Generate script to create required directories."""
    return textwrap.dedent(f"""\
        mkdir -p {CONTAINER_SPACK_PROJECT_DIR} \\
                 {CONTAINER_SPACK_TEMPLATES_DIR} \\
                 {CONTAINER_SLURM_DIR} \\
                 {CONTAINER_SPACK_CACHE_DIR}
    """).strip()


def get_spack_build_script() -> str:
    """Generate script to build Slurm with Spack."""
    return textwrap.dedent(f"""\
        bash -c "source {SPACK_SETUP_SCRIPT} && \\
        spack env activate . && \\
        rm -f spack.lock && \\
        spack concretize -j \\$(nproc) -f --fresh && \\
        spack install -j\\$(nproc) --only-concrete -f --verbose -p 4 --no-cache && \\
        spack env view regenerate && \\
        spack module lmod refresh --delete-tree -y && \\
        spack module lmod refresh -y && \\
        mkdir -p {CONTAINER_SLURM_DIR}/modules && \\
        SPACK_ROOT_PATH=\\$(spack location -r) && \\
        for f in \\$(find \\$SPACK_ROOT_PATH/share/spack/lmod -type f -name '*.lua'); do \\
            case \\$f in *slurm*) cp \\"\\$f\\" {CONTAINER_SLURM_DIR}/modules/;; esac; \\
        done"
    """).strip()


def get_package_tarball_script(modulerc_script: str, version: str) -> str:
    """
    Generate script to package everything into a tarball.

    Args:
        modulerc_script: The script to create .modulerc.lua file
        version: Slurm version (e.g., "25.05") for the tarball filename

    """
    return textwrap.dedent(f"""\
        set -e && \\
        [ -d "{CONTAINER_SLURM_DIR}/view" ] || {{ \\
            echo "ERROR: Spack view was not created at {CONTAINER_SLURM_DIR}/view"; \\
            exit 1; \\
        }} && \\
        MISSING_LIBS="" && \\
        for lib in libmunge.so libjwt.so libjansson.so; do \\
            if ! find {CONTAINER_SLURM_DIR}/view/lib* -name "$lib*" 2>/dev/null | grep -q .; then \\
                echo "WARNING: $lib not found in view" && \\
                MISSING_LIBS="$MISSING_LIBS $lib"; \\
            fi; \\
        done && \\
        if [ -n "$MISSING_LIBS" ]; then \\
            echo "WARNING: Some expected libraries/binaries are missing: $MISSING_LIBS" && \\
            echo "Continuing anyway - they may not be required for this configuration"; \\
        else \\
            echo "DEBUG: All critical libraries verified in view"; \\
        fi && \\
        echo "DEBUG: Packaging view directly (projections create FHS layout)..." && \\
        cd {CONTAINER_SLURM_DIR}/view && \\
        find . -name "include" -type d -exec rm -rf {{}} + 2>/dev/null || true && \\
        find . -path "*/lib/pkgconfig" -type d -exec rm -rf {{}} + 2>/dev/null || true && \\
        find . -path "*/share/doc" -type d -exec rm -rf {{}} + 2>/dev/null || true && \\
        find . -path "*/share/man" -type d -exec rm -rf {{}} + 2>/dev/null || true && \\
        find . -path "*/share/info" -type d -exec rm -rf {{}} + 2>/dev/null || true && \\
        find . -name "__pycache__" -type d -exec rm -rf {{}} + 2>/dev/null || true && \\
        find . -name "*.pyc" -delete 2>/dev/null || true && \\
        find . -name "*.a" -delete 2>/dev/null || true && \\
        mkdir -p assets && \\
        cp -r {CONTAINER_SLURM_DIR}/slurm_assets assets/ && \\
        mkdir -p assets/modules/slurm && \\
        cp {CONTAINER_SLURM_DIR}/modules/*.lua assets/modules/slurm/ && \\
        {modulerc_script} && \\
        cd {CONTAINER_SLURM_DIR} && \\
        mkdir -p {CONTAINER_SLURM_DIR}/redistributable && \\
        tar -chzf {CONTAINER_SLURM_DIR}/redistributable/slurm-{version}-software.tar.gz view && \\
        mkdir -p {CONTAINER_BUILD_OUTPUT_DIR} && \\
        cp {CONTAINER_SLURM_DIR}/redistributable/slurm-{version}-software.tar.gz {CONTAINER_BUILD_OUTPUT_DIR}/
    """).strip()


def get_dockerfile(spack_yaml_content: str, version: str = "25.05") -> str:
    """
    Generate a multi-stage Dockerfile for building Slurm packages.

    Stage 1 (init): Ubuntu + system deps + Spack (heavily cached)
    Stage 2 (builder): Runs spack install, creates view, generates modules (cached on spack.yaml)
    Stage 3 (packager): Copies slurm_assets and creates tarball (invalidates on asset changes)

    Args:
        spack_yaml_content: The complete spack.yaml content as a string
        version: Slurm version (e.g., "25.05") for the tarball filename

    Returns:
        A complete multi-stage Dockerfile as a string

    """
    # Generate all script components
    install_deps_script = get_install_system_deps_script()
    install_spack_script = get_install_spack_script()
    spack_profile_script = get_spack_profile_script()
    create_dirs_script = get_create_directories_script()
    module_template_content = get_module_template_content()
    spack_build_script = get_spack_build_script()

    # Generate the modulerc creation script
    modulerc_script = get_modulerc_creation_script(
        module_dir=f"{CONTAINER_SLURM_DIR}/view/assets/modules/slurm",
        modulerc_path=f"{CONTAINER_SLURM_DIR}/view/assets/modules/slurm/.modulerc.lua",
    )

    # Generate the packaging script
    package_script = get_package_tarball_script(modulerc_script, version)

    return textwrap.dedent(
        f"""\
# Slurm Factory Build Container - Multi-Stage Build
# Generated by slurm-factory - DO NOT EDIT MANUALLY

# ========================================================================
# Stage 1: Init - Base system with Spack (heavily cached)
# ========================================================================
FROM ubuntu:24.04 AS init

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=UTC

# Install minimal system dependencies for Spack
RUN {install_deps_script}

# Install Spack v1.0.0
RUN {install_spack_script}

ENV SPACK_ROOT=/opt/spack
ENV PATH=$SPACK_ROOT/bin:$PATH
RUN {spack_profile_script}

# Create required directories
RUN {create_dirs_script}

# ========================================================================
# Stage 2: Builder - Compile Slurm (cached on spack.yaml changes)
# ========================================================================
FROM init AS builder

# Copy spack.yaml (invalidates cache when build spec changes)
RUN cat > {CONTAINER_SPACK_PROJECT_DIR}/spack.yaml << 'SPACK_YAML_EOF'
{spack_yaml_content}
SPACK_YAML_EOF

# Copy module template (Spack expects it in modules/ subdirectory)
RUN mkdir -p {CONTAINER_SPACK_TEMPLATES_DIR}/modules
RUN cat > {CONTAINER_SPACK_TEMPLATES_DIR}/modules/relocatable_modulefile.lua << 'MODULE_TEMPLATE_EOF'
{module_template_content}
MODULE_TEMPLATE_EOF

WORKDIR {CONTAINER_SPACK_PROJECT_DIR}
# Build Slurm: install + create view + generate modules
RUN {spack_build_script}



# ========================================================================
# Stage 3: Packager - Create tarball (invalidates on asset changes)
# ========================================================================
FROM builder AS packager

# Use bash as the shell for RUN commands in this stage
SHELL ["/bin/bash", "-c"]

# Copy configuration assets (invalidates cache when they change)
COPY data/slurm_assets/ {CONTAINER_SLURM_DIR}/slurm_assets/

# Package everything into single tarball
RUN {package_script}

CMD ["/bin/bash"]
"""
    )
