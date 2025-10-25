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
Dynamic Spack environment configuration generator for slurm-factory.

This module generates Spack environment configurations as Python dictionaries,
allowing for easy parameterization of Slurm versions and GPU support options.
"""

from typing import Any, Dict

from slurm_factory.constants import SLURM_VERSIONS

# Template name for relocatable module files (relative to Spack templates directory)
TEMPLATE_NAME = "modules/relocatable_modulefile.lua"


def generate_module_config(
    slurm_version: str = "25.05",
    gpu_support: bool = False,
    minimal: bool = False,
) -> Dict[str, Any]:
    """
    Generate the Lmod module configuration section for Spack.

    Args:
        slurm_version: Slurm version to build (25.05, 24.11, 23.11, 23.02)
        gpu_support: Whether to include GPU support (NVML, RSMI)
        minimal: Whether to build minimal Slurm (without OpenMPI and extra features)

    Returns:
        Dictionary representing the modules configuration section

    """
    if slurm_version not in SLURM_VERSIONS:
        raise ValueError(
            f"Unsupported Slurm version: {slurm_version}. Supported versions: {list(SLURM_VERSIONS.keys())}"
        )

    slurm_package_version = SLURM_VERSIONS[slurm_version]

    # Build type description for metadata
    if minimal:
        build_type = "minimal build"
    elif gpu_support:
        build_type = "GPU-enabled build"
    else:
        build_type = "standard build"

    # Base module configuration
    modules_config: Dict[str, Any] = {
        "default": {
            "enable": ["lmod"],
            "lmod": {
                "core_compilers": ["gcc@13.3.0"],  # Mark gcc as core for relocatable binaries
                "hierarchy": [],  # Flat hierarchy for simpler deployment
                "include": (
                    ["slurm", "openmpi", "mysql"] if not minimal else ["slurm"]
                ),  # Include OpenMPI for full builds
                "slurm": {
                    "template": TEMPLATE_NAME,  # Apply our custom template only to Slurm
                    "autoload": "direct",
                    "conflict": ["{name}"],
                    "environment": {
                        "set": {
                            # Allow runtime override with environment variable fallback
                            "SLURM_CONF": "/etc/slurm/slurm.conf",
                            "SLURM_ROOT": "{prefix}",
                            # Add build-specific metadata
                            "SLURM_BUILD_TYPE": build_type,
                            "SLURM_VERSION": slurm_package_version,
                            # Add dynamic prefix support for redistributable packages
                            "SLURM_PREFIX": "{prefix}",
                            # Add hint for users about customization capability
                            "SLURM_MODULE_HELP": (
                                "Set SLURM_INSTALL_PREFIX before loading to override installation path"
                            ),
                            # Explicit compiler information for relocatability tracking
                            "SLURM_COMPILER": "{compiler.name}@{compiler.version}",
                            "SLURM_TARGET_ARCH": "{architecture}",
                            # GCC runtime prefix for relocatability (avoid guessing libdir)
                            "SLURM_GCC_RUNTIME_PREFIX": "{^gcc-runtime.prefix}",
                        },
                        "prepend_path": {
                            # Rely on RPATH/RUNPATH for library discovery - no LD_LIBRARY_PATH needed
                            "PATH": "{prefix}/bin:{prefix}/sbin",
                            "CPATH": "{prefix}/include",
                            "PKG_CONFIG_PATH": "{prefix}/lib/pkgconfig",
                            "MANPATH": "{prefix}/share/man",
                            "CMAKE_PREFIX_PATH": "{prefix}",
                        },
                    },
                },
            },
        },
    }

    # Remove unnecessary GPU PATH duplication - RPATH covers libs and PATH already includes {prefix}/bin
    if gpu_support:
        pass  # nothing to add here; RPATH covers libs and PATH already includes {prefix}/bin

    # Configure OpenMPI module behavior based on build type
    if not minimal:
        modules_config["default"]["lmod"]["openmpi"] = {"environment": {"set": {"OMPI_MCA_plm": "slurm"}}}

    return modules_config


def generate_spack_config(
    slurm_version: str = "25.05",
    gpu_support: bool = False,
    minimal: bool = False,
    install_tree_root: str = "/opt/slurm/software",
    view_root: str = "/opt/slurm/view",  # Use separate view directory
    buildcache_root: str = "/opt/slurm-factory-cache/spack-buildcache",
    sourcecache_root: str = "/opt/slurm-factory-cache/spack-sourcecache",
    binary_index_root: str = "/opt/slurm-factory-cache/binary_index",
    additional_variants: str = "",
    enable_verification: bool = False,
) -> Dict[str, Any]:
    """
    Generate a Spack environment configuration dictionary.

    Args:
        slurm_version: Slurm version to build (25.05, 24.11, 23.11, 23.02)
        gpu_support: Whether to include GPU support (NVML, RSMI)
        minimal: Whether to build minimal Slurm (without OpenMPI and extra features)
        install_tree_root: Root directory for Spack installations
        view_root: Root directory for Spack view
        buildcache_root: Directory for binary build cache
        sourcecache_root: Directory for source cache
        binary_index_root: Directory for binary index
        additional_variants: Additional Spack variants to add to the Slurm spec
        enable_verification: Whether to enable relocatability verification checks

    Returns:
        Dictionary representing the Spack environment configuration

    """
    if slurm_version not in SLURM_VERSIONS:
        raise ValueError(
            f"Unsupported Slurm version: {slurm_version}. Supported versions: {list(SLURM_VERSIONS.keys())}"
        )

    slurm_package_version = SLURM_VERSIONS[slurm_version]

    # Build Slurm spec with conditional features
    gpu_flags = "+nvml +rsmi" if gpu_support else "~nvml ~rsmi"

    gcc_spec = "gcc-runtime@13.3.0 %gcc@13.3.0"
    openldap_spec = "openldap@2.6.8+client_only~perl+sasl+dynamic+shared~static tls=openssl %gcc@13.3.0"
    curl_spec = (
        "slurm_factory.curl@8.15.0+nghttp2+libssh2+libssh+gssapi+ldap+librtmp+libidn2 "
        "libs=shared,static tls=openssl %gcc@13.3.0"
    )
    specs = [
        # Build a bootstrapped compiler first (in-DAG)
        gcc_spec,
        openldap_spec,  # Build openldap before curl since curl+ldap needs it
        curl_spec,
        "patchelf@0.18.0 %gcc@13.3.0",  # For RPATH fixing during relocatability
    ]
    if minimal:
        specs.append(
            f"slurm_factory.slurm@{slurm_package_version} +readline ~hwloc ~pmix ~restd "
            f"{gpu_flags} ~cgroup sysconfdir=/etc/slurm %gcc@13.3.0"
        )
    else:
        specs.append("zlib@1.3.1 %gcc@13.3.0")
        specs.append("openmpi@5.0.3 schedulers=slurm fabrics=auto %gcc@13.3.0")
        specs.append("pmix@5.0.8 ~munge ~python %gcc@13.3.0")
        specs.append("mysql@8.0.35+client_only %gcc@13.3.0")
        specs.append("hdf5@1.14.6 +hl +cxx %gcc@13.3.0")
        specs.append(
            f"slurm_factory.slurm@{slurm_package_version} {additional_variants} "
            "+readline +hwloc +pmix +hdf5 +kafka +restd +cgroup +pam "
            f"{gpu_flags} sysconfdir=/etc/slurm %gcc@13.3.0"
        )

    # Base view packages (runtime dependencies + toolchain for relocatability)
    view_packages = [
        "slurm",
        "readline",
        "pkgconf",  # Modern pkg-config implementation
        "hwloc",
        "libpciaccess",
        "xz",
        "libiconv",
        "libxml2",
        "lz4",
        "numactl",
        "gcc-runtime",
        "http-parser",
        "ca-certificates-mozilla",  # Self-contained SSL certificates for relocatability
        "curl",
        "libssh2",  # SSH2 library needed by curl and slurmd
        "openldap",  # LDAP library needed by curl
        "openssl",  # SSL/TLS library
        "munge",  # Authentication library
        "json-c",  # JSON parsing library
        "libjwt",  # JWT token library for REST API
        "jansson",  # JSON library required by libjwt
        "glib",  # GLib library
        "zlib",  # Standard zlib compression library (provides libz.so.1)
        "zlib-ng",  # Compression library
        "librdkafka",
        "rapidjson",
        "cyrus-sasl",
        "patchelf",  # For RPATH fixing during relocatability
        "ncurses",  # Terminal library for libtinfow
        "lua",  # Lua scripting language for Slurm plugin support
    ]

    # Add conditional packages based on build type
    if not minimal:
        # Full builds include openmpi, pmix, and mysql
        view_packages.extend(["openmpi", "pmix", "libevent", "mysql"])

    if gpu_support:
        view_packages.extend(["cuda", "rocm"])

    # Base configuration
    config: Dict[str, Any] = {
        "spack": {
            "specs": specs,
            "repos": {
                "slurm_factory": {
                    "git": "https://github.com/vantagecompute/slurm-factory-spack-repo.git",
                    "branch": "main",
                },
            },
            "concretizer": {
                "unify": True,  # Unify specs (Spack 1.x feature)
                "reuse": False,  # Don't reuse installed packages - build from source
            },
            # Force all packages to be buildable from source
            "packages": {
                "all": {
                    "target": ["x86_64_v3"],
                    "require": "target=x86_64_v3",
                    "buildable": True,
                },
                "cmake": {
                    "externals": [{"spec": "cmake@3.28.3", "prefix": "/usr"}],
                    "buildable": False,
                    "require": "@3.28.3",
                },
                "python": {
                    "externals": [{"spec": "python@3.12.3", "prefix": "/usr"}],
                    "buildable": False,
                    "require": "@3.12.3",
                },
                "autoconf": {
                    "externals": [{"spec": "autoconf@2.71", "prefix": "/usr"}],
                    "buildable": False,
                },
                "automake": {
                    "externals": [{"spec": "automake@1.16.5", "prefix": "/usr"}],
                    "buildable": False,
                },
                "libtool": {
                    "externals": [{"spec": "libtool@2.4.7", "prefix": "/usr"}],
                    "buildable": False,
                },
                "gmake": {"externals": [{"spec": "gmake@4.3", "prefix": "/usr"}], "buildable": False},
                "m4": {"externals": [{"spec": "m4@1.4.18", "prefix": "/usr"}], "buildable": False},
                "pkgconf": {"externals": [{"spec": "pkgconf@1.8.1", "prefix": "/usr"}], "buildable": False},
                "diffutils": {
                    "externals": [{"spec": "diffutils@3.10", "prefix": "/usr"}],
                    "buildable": False,
                },
                "findutils": {
                    "externals": [{"spec": "findutils@4.9.0", "prefix": "/usr"}],
                    "buildable": False,
                },
                "gettext": {"externals": [{"spec": "gettext@0.21", "prefix": "/usr"}], "buildable": False},
                "tar": {"externals": [{"spec": "tar@1.34", "prefix": "/usr"}], "buildable": False},
                # Build xz and bzip2 from source to avoid library version conflicts
                "xz": {"buildable": True},
                "bzip2": {"buildable": True},
                # Runtime libraries that must be built for Slurm linking
                # These are critical dependencies that Slurm links against at runtime
                "munge": {"buildable": True},  # Authentication - let Spack pick latest available
                "json-c": {"buildable": True},  # JSON parsing - linked at runtime
                "libpciaccess": {"buildable": True},  # PCI access library
                "cyrus-sasl": {
                    "buildable": True,
                },
                "rapidjson": {"buildable": True},
                "openldap": {
                    "buildable": True,
                    "version": ["2.6.8"],
                },
                "curl": {
                    "buildable": True,
                    "version": ["8.15.0"],
                    "variants": "libs=shared,static tls=openssl",
                },
                "openssl": {
                    "buildable": True,
                    "version": ["3:"],
                    "variants": "~docs +shared ~static",  # Remove system cert dependencies
                    "require": ["^ca-certificates-mozilla"],  # Force use of Spack certs
                },
                "ca-certificates-mozilla": {"buildable": True},  # Self-contained SSL certificates
                "readline": {"buildable": True},  # Interactive command line
                "ncurses": {"buildable": True},  # Terminal control for readline
                "lz4": {"buildable": True},  # Fast compression - linked at runtime
                "zlib-ng": {
                    "buildable": True,
                    "variants": "+compat",
                },  # zlib-ng with zlib compatibility - linked at runtime
                "hwloc": {"buildable": True, "version": ["2:"]},  # Hardware topology - use hwloc 2.x series
                "numactl": {"buildable": True},  # NUMA support - used by Slurm for memory binding
                # Build ALL system libraries from source for complete isolation
                "dbus": {
                    "buildable": True,
                    "variants": "system-socket=/var/run/dbus/system_bus_socket",
                },
                "glib": {"buildable": True},
                "libxml2": {"buildable": True},
                # Build these inside Spack to avoid Perl XS module linking to external system libraries
                "gdbm": {"buildable": True},
                "berkeley-db": {"buildable": True},
                # Force Perl to use Spack-built dependencies for XS modules
                "perl": {"require": ["^bzip2", "^gdbm", "^berkeley-db"]},
                "libgcrypt": {"buildable": True},
                "libgpg-error": {"buildable": True},
                # Additional REST API dependencies - build for relocatability
                "http-parser": {"buildable": True},  # HTTP parsing for REST API
                "libjwt": {
                    "buildable": True,
                    "require": [
                        "^openssl@3:",
                        "^jansson",
                    ],  # Ensure it uses Spack-built OpenSSL 3.x and jansson
                },  # JWT token support - essential for Slurm REST API
                # MySQL client library for Slurm accounting storage
                "mysql": {"buildable": True, "variants": "+client_only"},
                "librdkafka": {
                    "buildable": True,
                },
                # PMIx configuration for consistent version
                "pmix": {
                    "buildable": True,
                    "version": ["5.0.8"],
                    "variants": "~munge ~python",  # Removed +shared as it doesn't exist
                },
                "libsigsegv": {"buildable": True},
                "hdf5": {"buildable": True},
                # Runtime-linked libraries: build with Spack for true relocatability
                # These may be linked by Slurm or its dependencies at runtime
                "linux-pam": {"buildable": True},  # Slurm PAM authentication
                "libevent": {"buildable": True},  # Used by PMIx and OpenMPI
                "jansson": {"buildable": True},  # JSON parsing for some Slurm features (shared is default)
                "libyaml": {"buildable": True},  # Configuration parsing
                # NOTE: bzip2 and xz are configured as external packages above to avoid library conflicts
                "zstd": {"buildable": True},  # Fast compression (transitive)
                # GCC compiler - prevent external detection to avoid multiple compiler hashes
                "gcc": {
                    "buildable": False,
                    "externals": [
                        {
                            "spec": "gcc@13.3.0 languages:='c,c++,fortran'",
                            "prefix": "/usr",
                            "extra_attributes": {
                                "compilers": {
                                    "c": "/usr/bin/gcc",
                                    "cxx": "/usr/bin/g++",
                                    "fortran": "/usr/bin/gfortran",
                                },
                                "environment": {},
                            },
                        },
                    ],
                },
                # GCC runtime (needed for dynamic linking)
                # GCC runtime for relocatable binaries (Spack 1.x approach)
                "gcc-runtime": {"buildable": True, "externals": []},
                "slurm": {
                    "version": [slurm_package_version],
                    "buildable": True,
                    "variants": "+shared ~static +pic",  # Consistent shared library preference
                    "prefer": ["slurm_factory.slurm"],  # Prefer our custom namespace
                },
                # OpenMPI configuration for consistent build
                "openmpi": {
                    "buildable": True,
                    "version": ["5.0.3"],
                    "variants": "schedulers=slurm fabrics=auto",
                },
            },
            "develop": {},
            "view": {
                "default": {
                    "root": view_root,
                    "link_type": "hardlink",  # Use hardlinks instead of symlinks for easier copying
                    "select": view_packages,  # Only include essential runtime dependencies in view
                    "exclude": ["^cmake", "^autoconf", "^automake", "^libtool", "^bison", "^flex"],
                }
            },
            "config": {
                "install_tree": {
                    "root": install_tree_root,
                    "padded_length": 0,  # Short, portable install paths for relocatability
                    "projections": {
                        "all": "{name}-{version}-{hash:7}"  # Short paths for better relocatability
                    },
                },
                # "build_stage": "/tmp/spack-stage",
                # "misc_cache": sourcecache_root,
                # "binary_index_root": binary_index_root,
                "checksum": True,
                "deprecated": True,
                # Spack 1.x performance enhancements
                "build_jobs": 4,  # Parallel build jobs
                "ccache": True,  # Disable ccache if not present
                "connect_timeout": 30,  # Network timeout for downloads
                "verify_ssl": True,  # Security setting
                "suppress_gpg_warnings": False,  # Show GPG warnings
                "shared_linking": {
                    "type": "rpath",  # Use RPATH for relocatable binaries (Spack 1.x)
                    "bind": False,  # Don't bind absolute paths - allow relocation
                    "missing_library_policy": "warn",  # Ignore on missing system
                },
            },
            "mirrors": {
                # Only use spack-public mirror for source downloads, not binaries
                # In single-stage builds, we build everything from source
                "spack-public": {"url": "https://mirror.spack.io", "signed": False},
            },
            "compilers": [
                {
                    "compiler": {
                        "spec": "gcc@=13.3.0",
                        "paths": {
                            "cc": "/usr/bin/gcc",
                            "cxx": "/usr/bin/g++",
                            "f77": "/usr/bin/gfortran",
                            "fc": "/usr/bin/gfortran",
                        },
                        "operating_system": "ubuntu24.04",
                        "target": "x86_64",
                        "modules": [],
                        "environment": {},
                        "extra_rpaths": [],
                    }
                }
            ],
            "modules": generate_module_config(slurm_version, gpu_support, minimal),
        }
    }

    # Add MPI provider configuration only for full builds (when OpenMPI is included)
    if not minimal:
        config["spack"]["packages"]["all"]["providers"] = {"mpi": ["openmpi"]}

    # Add verification settings if enabled (useful for CI and pre-release checks)
    if enable_verification:
        config["spack"]["config"]["verify"] = {
            "relocatable": True,  # Verify binaries are relocatable
            "dependencies": True,  # Verify all dependencies are present
            "shared_libraries": True,  # Check shared library dependencies
        }

    return config


def get_comment_header(slurm_version: str, gpu_support: bool, minimal: bool = False) -> str:
    """Generate a descriptive comment header for the configuration."""
    if minimal:
        desc = "(minimal build - basic Slurm only)"
    elif gpu_support:
        desc = "with GPU support"
    else:
        desc = "(optimized for minimal runtime footprint)"
    return f"# Spack environment for building Slurm {slurm_version} {desc}"


def generate_yaml_string(
    slurm_version: str = "25.05",
    gpu_support: bool = False,
    minimal: bool = False,
    additional_variants: str = "",
    enable_verification: bool = False,
) -> str:
    """
    Generate a YAML string representation of the Spack environment configuration.

    Args:
        slurm_version: Slurm version to build
        gpu_support: Whether to include GPU support
        minimal: Whether to build minimal Slurm
        additional_variants: Additional Spack variants to include
        enable_verification: Whether to enable relocatability verification checks

    Returns:
        YAML string representation of the configuration

    """
    import yaml

    config = generate_spack_config(
        slurm_version=slurm_version,
        gpu_support=gpu_support,
        minimal=minimal,
        additional_variants=additional_variants,
        enable_verification=enable_verification,
    )
    header = get_comment_header(slurm_version, gpu_support, minimal)

    # Generate YAML with proper formatting
    yaml_content = yaml.dump(config, default_flow_style=False, sort_keys=False, indent=2)

    return f"{header}\n{yaml_content}"


# Convenience functions for common configurations
def cpu_only_config(slurm_version: str = "25.05", enable_verification: bool = False) -> Dict[str, Any]:
    """Generate CPU-only configuration (default, optimized for size)."""
    return generate_spack_config(
        slurm_version=slurm_version, gpu_support=False, minimal=False, enable_verification=enable_verification
    )


def gpu_enabled_config(slurm_version: str = "25.05", enable_verification: bool = False) -> Dict[str, Any]:
    """Generate GPU-enabled configuration (larger, includes CUDA/ROCm)."""
    return generate_spack_config(
        slurm_version=slurm_version, gpu_support=True, minimal=False, enable_verification=enable_verification
    )


def minimal_config(slurm_version: str = "25.05", enable_verification: bool = False) -> Dict[str, Any]:
    """Generate minimal configuration (smallest, basic Slurm only)."""
    return generate_spack_config(
        slurm_version=slurm_version, gpu_support=False, minimal=True, enable_verification=enable_verification
    )


def verification_config(slurm_version: str = "25.05", gpu_support: bool = False) -> Dict[str, Any]:
    """Generate configuration with verification enabled (for CI and pre-release checks)."""
    return generate_spack_config(
        slurm_version=slurm_version, gpu_support=gpu_support, minimal=False, enable_verification=True
    )


if __name__ == "__main__":
    # Example usage - generate configurations for testing
    print("=== CPU-only Slurm 25.05 ===")
    print(generate_yaml_string("25.05", False, False))

    print("\n=== GPU-enabled Slurm 25.05 ===")
    print(generate_yaml_string("25.05", True, False))

    print("\n=== Minimal Slurm 25.05 ===")
    print(generate_yaml_string("25.05", gpu_support=False, minimal=True))

    print("\n=== CPU-only Slurm 25.05 with Verification (CI) ===")
    print(generate_yaml_string("25.05", gpu_support=False, minimal=False, enable_verification=True))
