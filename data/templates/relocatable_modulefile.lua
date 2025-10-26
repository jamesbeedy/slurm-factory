-- Copyright 2025 Vantage Compute Corporation
--
-- Licensed under the Apache License, Version 2.0 (the "License");
-- you may not use this file except in compliance with the License.
-- You may obtain a copy of the License at
--
--     http://www.apache.org/licenses/LICENSE-2.0
--
-- Unless required by applicable law or agreed to in writing, software
-- distributed under the License is distributed on an "AS IS" BASIS,
-- WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
-- See the License for the specific language governing permissions and
-- limitations under the License.

-- -*- lua -*-
-- Module file created by spack (https://github.com/spack/spack)
{% if spec -%}
-- {{ spec.short_spec }}
{% else -%}
-- Package information not available
{% endif -%}
--

{% if spec and spec.name -%}
whatis([[Name : {{ spec.name }}]])
{% else -%}
whatis([[Name : slurm]])
{% endif -%}
{% if spec and spec.version -%}
whatis([[Version : {{ spec.version }}]])
{% else -%}
whatis([[Version : unknown]])
{% endif -%}
whatis([[Short description : Slurm workload manager]])
{% if spec and spec.name -%}
help([[Name   : {{ spec.name }}]])
{% else -%}
help([[Name   : slurm]])
{% endif -%}
{% if spec and spec.version -%}
help([[Version: {{ spec.version }}]])
{% else -%}
help([[Version: unknown]])
{% endif -%}
help([[
Slurm is an open-source workload manager designed for Linux clusters of
all sizes. This is a relocatable module that allows installation at
any prefix by setting SLURM_INSTALL_PREFIX environment variable.

Relocatability Features:
- Binaries prefer RPATH for library discovery when properly relocated
- Falls back to LD_LIBRARY_PATH for incomplete RPATH relocation scenarios  
- Can be relocated by setting SLURM_INSTALL_PREFIX before loading module
- Self-contained installation with all runtime dependencies included
- Compatible with containerized and distributed deployments

Usage:
  module load slurm                    # Use default installation path
  export SLURM_INSTALL_PREFIX=/new/path && module load slurm  # Use custom path

Note: For optimal performance, ensure binaries were installed via Spack build cache
for proper RPATH relocation. Manual copying may require LD_LIBRARY_PATH fallback.
]])

-- Relocatable prefix logic with validation
local slurm_prefix = os.getenv("SLURM_INSTALL_PREFIX")
if not slurm_prefix then
    slurm_prefix = "/opt/slurm/view"
end

-- Validate that the specified prefix exists and contains Slurm
local slurm_bin = pathJoin(slurm_prefix, "bin", "scontrol")
if not isFile(slurm_bin) then
    LmodError("Slurm installation not found at: " .. slurm_prefix .. 
              "\nExpected to find: " .. slurm_bin ..
              "\nPlease check SLURM_INSTALL_PREFIX or use default installation.")
end

-- Basic environment setup based on standard Slurm installation layout
prepend_path("PATH", pathJoin(slurm_prefix, "bin"))
prepend_path("PATH", pathJoin(slurm_prefix, "sbin"))
prepend_path("MANPATH", pathJoin(slurm_prefix, "share/man"))

-- Development support (if headers are available)
prepend_path("CPATH", pathJoin(slurm_prefix, "include"))
prepend_path("PKG_CONFIG_PATH", pathJoin(slurm_prefix, "lib/pkgconfig"))
prepend_path("CMAKE_PREFIX_PATH", slurm_prefix)

-- Library path handling with fallback for incomplete RPATH relocation
-- Relocatable binaries should use RPATH, but provide LD_LIBRARY_PATH fallback
-- This ensures compatibility when RPATH relocation fails or is incomplete
local lib_paths = {
    pathJoin(slurm_prefix, "lib"),
    pathJoin(slurm_prefix, "lib64"), 
    pathJoin(slurm_prefix, "lib/slurm")
}

-- Only add library paths that actually exist to avoid cluttering environment
for _, lib_path in ipairs(lib_paths) do
    if isDir(lib_path) then
        prepend_path("LD_LIBRARY_PATH", lib_path)
    end
end

-- Set important Slurm-specific environment variables
setenv("SLURM_INSTALL_PREFIX", slurm_prefix)
setenv("SLURM_ROOT", slurm_prefix)

-- Configuration paths (can be overridden by setting SLURM_CONF)
local slurm_conf = os.getenv("SLURM_CONF")
if not slurm_conf then
    -- Default to sysconfdir if it exists, otherwise use etc/slurm under prefix
    local default_conf = "/etc/slurm/slurm.conf"

    if isFile(default_conf) then
        setenv("SLURM_CONF", default_conf)
    else
        -- Set the variable but warn if config doesn't exist
        setenv("SLURM_CONF", default_conf)
        if mode() == "load" then
            LmodMessage("Warning: Slurm configuration file not found at " .. default_conf)
            LmodMessage("You may need to create slurm.conf or set SLURM_CONF manually")
        end
    end
end

-- Relocatability metadata (for troubleshooting and deployment tools)
{% if spec and spec.compiler -%}
setenv("SLURM_BUILD_COMPILER", "{{ spec.compiler }}")
{% endif -%}
{% if spec and spec.target -%}
setenv("SLURM_BUILD_TARGET", "{{ spec.target }}")
{% endif -%}
setenv("SLURM_BUILD_TYPE", "relocatable")

-- SSL certificate handling for relocatable OpenSSL
local ssl_cert_dir = pathJoin(slurm_prefix, "etc/ssl/certs")
local ssl_cert_file = pathJoin(slurm_prefix, "etc/ssl/cert.pem")

if isDir(ssl_cert_dir) then
    setenv("SSL_CERT_DIR", ssl_cert_dir)
end
if isFile(ssl_cert_file) then
    setenv("SSL_CERT_FILE", ssl_cert_file)
end

-- Module identification and conflict resolution
{% if spec and spec.name and spec.version -%}
local version = "{{ spec.version }}"
local name = "{{ spec.name }}"
{% else -%}
local version = "25.05"
local name = "slurm"
{% endif -%}

-- Prevent loading multiple Slurm modules simultaneously
conflict(name)

-- Family support for better module management
family("workloadmanager")

-- Module load/unload messages
if mode() == "load" then
    LmodMessage("Loading Slurm " .. version .. " from: " .. slurm_prefix)
elseif mode() == "unload" then
    LmodMessage("Unloading Slurm " .. version)
end
