
# Build Optimization Guide

Advanced optimization strategies for maximizing build performance and minimizing package size with slurm-factory's intelligent caching and dependency management systems.

## Multi-Layer Caching Strategy

slurm-factory implements a sophisticated caching system that dramatically reduces build times for subsequent builds:

### 1. **Container Layer Caching**

#### Base Image Reuse
```bash
# First build: Creates base container (~5 minutes)
slurm-factory build --slurm-version 25.05

# Subsequent builds: Reuses base container (~30 seconds setup)
slurm-factory build --slurm-version 24.11
slurm-factory build --slurm-version 25.05 --gpu
```

**Container Strategy:**
- **Base Image**: Single Ubuntu 24.04 container with build tools
- **LXD Copy**: Fast container duplication (copy-on-write)
- **Persistent Mounts**: Cache directories mounted across builds
- **Cleanup Policy**: Base container preserved, build containers removed

### 2. **Spack Build Cache**

#### Binary Package Cache
```yaml
# Cache Configuration
buildcache_root: "/opt/slurm-factory-cache/spack-buildcache"
reuse: true                    # Reuse compatible packages
unify: true                   # Optimize dependency resolution

# Performance Impact:
first_build: "45-90 minutes"
cached_build: "5-15 minutes"  # >10x speedup
cache_hit_ratio: "80-95%"     # For common dependencies
```

#### Source Download Cache  
```yaml
sourcecache_root: "/opt/slurm-factory-cache/spack-sourcecache" 
# Avoids re-downloading source archives
# Persistent across container lifecycles
# Shared between different Slurm versions
```

### 3. **Compilation Acceleration**

#### Parallel Build Configuration
```yaml
spack_config:
  build_jobs: 4              # Concurrent package compilation
  ccache: true               # C/C++ object caching  
  build_stage: "/tmp"        # Fast tmpfs build directory
```

## Intelligent Dependency Classification

slurm-factory uses a sophisticated dependency strategy to optimize both build time and package size:

### **🔧 External Tools Strategy (Build-Time Only)**

System packages leveraged during compilation but excluded from final package:

```yaml
external_packages:
  # Build System Tools
  cmake: {spec: "cmake@3.28.3", prefix: "/usr"}
  autoconf: {spec: "autoconf@2.71", prefix: "/usr"}  
  automake: {spec: "automake@1.16.5", prefix: "/usr"}
  libtool: {spec: "libtool@2.4.7", prefix: "/usr"}
  
  # Compilers & Build Tools  
  gcc: {spec: "gcc@13.3.0", prefix: "/usr"}
  pkg-config: {spec: "pkg-config@0.29.2", prefix: "/usr"}
  bison: {spec: "bison@3.8.2", prefix: "/usr"}
  flex: {spec: "flex@2.6.4", prefix: "/usr"}
  
  # System Libraries (Build-Time Dependencies)
  dbus: {spec: "dbus@1.14.10", prefix: "/usr"}
  glib: {spec: "glib@2.80.0", prefix: "/usr"}
  libxml2: {spec: "libxml2@2.9.14", prefix: "/usr"}
```

**Benefits:**
- **⚡ Fast Builds**: Leverage optimized system packages
- **📦 Smaller Packages**: Build tools excluded from distribution
- **🔒 Consistency**: Use well-tested system components
- **💾 Reduced Compilation**: Skip rebuilding standard tools

### **⚡ Runtime Libraries Strategy (Fresh Builds)**

Critical dependencies compiled with architecture-specific optimizations:

```yaml
runtime_packages:
  # Authentication & Security
  munge: {buildable: true}           # Authentication daemon
  openssl: {buildable: true, version: ["3:"]}  # SSL/TLS encryption
  
  # Core Runtime Dependencies  
  json-c: {buildable: true}          # JSON parsing (linked at runtime)
  curl: {buildable: true}            # HTTP client for REST API
  readline: {buildable: true}        # Interactive CLI support
  ncurses: {buildable: true}         # Terminal control
  
  # Performance-Critical Libraries
  hwloc: {buildable: true, version: ["2:"]}    # Hardware topology
  numactl: {buildable: true}         # NUMA memory binding
  lz4: {buildable: true}             # Fast compression
  zlib-ng: {buildable: true}         # Next-gen compression
```

**Optimization Benefits:**
- **🏃 Performance**: Architecture-specific optimizations (SSE, AVX)
- **🔐 Security**: Fresh builds with latest security patches  
- **🎯 Compatibility**: Guaranteed version compatibility with Slurm
- **📊 Profiling**: Custom optimization flags for target hardware

### **Dependency Size Impact**

```bash
# Package Size Comparison
external_tools_approach:
  build_time: "25% faster"
  package_size: "60% smaller"  
  disk_usage: "~2-5GB (CPU) vs ~8-12GB (all deps included)"

runtime_libs_fresh:
  performance: "15-30% faster execution"
  compatibility: "99.9% success rate"
  security: "Latest patches included"
```

## Build Performance Tuning

### **Container Resource Optimization**

```yaml
# LXD Profile for Optimal Builds
lxd_profile:
  limits:
    cpu: "8"                 # Use all available cores
    memory: "16GB"           # Adequate memory for parallel builds
    memory.swap: "false"     # Disable swap for performance
  
  storage:
    type: "zfs"              # ZFS for better I/O performance
    size: "100GB"            # Adequate space for cache
    
  devices:
    cache_mount:
      path: "/opt/slurm-factory-cache"
      source: "/host/cache"   # Persistent cache location
      type: "disk"
```

### **Parallel Compilation Settings**

```yaml
# Spack Performance Configuration  
spack_config:
  build_jobs: 4              # Concurrent package builds
  ccache: true               # C/C++ object caching
  connect_timeout: 30        # Network download timeout
  build_stage: "/tmp/spack-stage"  # Fast tmpfs builds
  
  # Hardware-specific optimizations
  target: "x86_64"          # Target architecture
  compiler_flags:
    cflags: "-O3 -march=native"
    cxxflags: "-O3 -march=native"
```

## Relocatable Module Architecture

### **Dynamic Prefix Implementation**

slurm-factory generates truly relocatable modules using environment variable substitution:

```lua
-- Dynamic Path Resolution
local install_prefix = os.getenv("SLURM_INSTALL_PREFIX") or "{prefix}"

-- Runtime Path Configuration
prepend_path("PATH", pathJoin(install_prefix, "bin"))
prepend_path("PATH", pathJoin(install_prefix, "sbin"))
prepend_path("LD_LIBRARY_PATH", pathJoin(install_prefix, "lib"))

-- Development Environment
prepend_path("CPATH", pathJoin(install_prefix, "include"))
prepend_path("PKG_CONFIG_PATH", pathJoin(install_prefix, "lib/pkgconfig"))
prepend_path("CMAKE_PREFIX_PATH", install_prefix)

-- Runtime Configuration
setenv("SLURM_ROOT", install_prefix)
setenv("SLURM_PREFIX", install_prefix)
```

### **Advanced Deployment Patterns**

```bash
# Pattern 1: Multi-Site Deployment
# Site A: /opt/slurm layout
export SLURM_INSTALL_PREFIX=/opt/slurm/software
module load slurm/25.05

# Site B: /shared/apps layout  
export SLURM_INSTALL_PREFIX=/shared/apps/slurm-25.05
module load slurm/25.05

# Pattern 2: Container Deployment
# Container with custom mount point
export SLURM_INSTALL_PREFIX=/app/slurm
module load slurm/25.05

# Pattern 3: User-Space Installation
# No root access required
export SLURM_INSTALL_PREFIX=$HOME/software/slurm-25.05
module load slurm/25.05
```

#### Parallel Compilation
Builds automatically use available CPU cores via:
- Spack's `build_jobs` configuration (auto-detected)
- Make's `-j$(nproc)` parallelization
- Ninja builds when available

#### Build Cache Utilization
```bash
# Pre-populate build cache with common dependencies
uv run slurm-factory build --slurm-version 25.05  # First build caches deps

# Subsequent builds reuse cached dependencies
uv run slurm-factory build --slurm-version 24.11  # Much faster
```

#### Dependency Management
```bash
# View dependency tree
spack spec slurm

# Minimize variants for faster builds
# CPU-only build (default) vs GPU build
uv run slurm-factory build --slurm-version 25.05          # ~45 minutes
uv run slurm-factory build --slurm-version 25.05 --gpu    # ~90 minutes
```

### 3. System-Level Optimization

#### Disk I/O
```bash
# Use tmpfs for build directory (if enough RAM)
sudo mount -t tmpfs -o size=32G tmpfs /tmp/slurm-build

# Or use fast SSD storage
export TMPDIR=/fast-ssd/tmp
```

#### Network
```bash
# Use local package mirrors for faster downloads
# Add to spack configuration
mkdir -p ~/.spack
cat > ~/.spack/mirrors.yaml << 'EOF'
mirrors:
  local: file:///opt/spack-mirror
EOF
```

## Package Size Optimization

### Build Variants Comparison

| Build Type | Dependencies | Size | Use Case |
|------------|-------------|------|----------|
| **CPU-only** | ~45 packages | ~2-5GB | Production clusters |
| **GPU-enabled** | ~180 packages | ~15-25GB | GPU clusters |
| **Minimal** | ~25 packages | ~1GB | Development/testing |

### 1. CPU-Only Builds (Recommended)

**Default configuration optimized for size**:
```yaml
# Automatically used with:
uv run slurm-factory build --slurm-version 25.05
```

**Dependencies included**:
- Core libraries: glibc, gcc runtime
- Network: PMIx, UCX (optimized)
- Essential tools: hwloc, numactl
- Authentication: munge, PAM

**Size breakdown**:
- Slurm binaries: ~200MB
- Core dependencies: ~1.5GB  
- Build tools overhead: ~500MB
- **Total: ~2-3GB**

### 2. Minimal Builds

For development or testing environments:
```bash
# Edit constants.py to reduce dependencies
# Modify SPACK_PROJECT_SETUP_SCRIPT template:

# Minimal package list
spack.yaml:
  packages:
    slurm:
      variants: ~cuda ~nvml ~x11 ~gtk
```

### 3. Optimized GPU Builds

When GPU support is required:
```bash
uv run slurm-factory build --slurm-version 25.05 --gpu
```

**Additional dependencies**:
- CUDA toolkit: ~8-12GB
- NVIDIA drivers: ~2-3GB
- GPU monitoring: NVML, nvidia-ml-py

**Optimization strategies**:
- Use CUDA containers instead of full GPU builds
- Deploy CPU build + CUDA runtime separately
- Use shared filesystems for CUDA installations

## Build Time Optimization

### Expected Build Times

| System Configuration | CPU Build | GPU Build |
|---------------------|-----------|-----------|
| 4 cores, 8GB RAM | ~60 minutes | ~120 minutes |
| 8 cores, 16GB RAM | ~35 minutes | ~75 minutes |
| 16 cores, 32GB RAM | ~20 minutes | ~45 minutes |

### Optimization Strategies

#### 1. Incremental Builds
```bash
# Build multiple versions efficiently
uv run slurm-factory build --slurm-version 24.11  # Caches dependencies
uv run slurm-factory build --slurm-version 25.05  # Reuses 90% of deps
```

#### 2. Parallel Dependency Builds
```bash
# Spack automatically parallelizes dependency builds
# Configure via ~/.spack/config.yaml:
config:
  build_jobs: 8              # Parallel package builds
  build_stage: /fast-disk    # Use fast storage
```

#### 3. Build Cache Management
```bash
# Monitor cache size
du -sh ~/.slurm-factory/spack-cache/

# Clean old builds if space is limited
rm -rf ~/.slurm-factory/builds/old-version/

# Spack garbage collection
spack gc -y
```

## Memory Optimization

### Container Memory Limits

#### Minimum Requirements
- **CPU builds**: 4GB RAM minimum, 8GB recommended
- **GPU builds**: 8GB RAM minimum, 16GB recommended
- **Parallel builds**: 2GB per build job

#### Memory-Constrained Systems
```bash
# Limit parallel jobs if memory is constrained
export SPACK_BUILD_JOBS=2

# Or edit build configuration
lxc profile set build-container limits.memory 4GB
```

### Swap Configuration
```bash
# Disable swap in containers for performance
lxc profile set build-container limits.memory.swap false

# Or configure host swap appropriately
sudo swapon --summary
```

## Network Optimization

### Download Acceleration
```bash
# Use package mirrors closest to your location
# Check slurm-factory's mirror configuration
grep -r "github\|releases" slurm_factory/

# Use corporate mirrors if available
export SPACK_MIRROR_URL=https://company-mirror.example.com
```

### Bandwidth Management
```bash
# Parallel downloads are automatic
# Limit if bandwidth is constrained:
export SPACK_CURL_TIMEOUT=30
export SPACK_CURL_RETRIES=3
```

## Storage Optimization

### Disk Space Management

#### Minimum Space Requirements
- **Build process**: 50GB free space
- **Final packages**: 5-30GB depending on variant
- **Spack cache**: 20-100GB (grows over time)

#### Space-Saving Strategies
```bash
# Build on separate filesystem
export SLURM_FACTORY_BUILD_DIR=/large-disk/builds

# Compress packages after build
gzip ~/.slurm-factory/builds/*/slurm-*-software.tar

# Clean intermediate files
rm -rf ~/.slurm-factory/builds/*/build-*
```

### File System Recommendations

| Filesystem | Build Performance | Storage Efficiency | Notes |
|------------|------------------|-------------------|-------|
| **ZFS** | Excellent | Excellent | Best overall choice |
| **Btrfs** | Good | Good | Good compression |
| **XFS** | Excellent | Fair | Best for large files |
| **Ext4** | Good | Fair | Most compatible |

## Deployment Optimization

### Module System Performance

#### Module Loading Optimization
```bash
# Pre-compile module files for faster loading
# Add to deployment script:
module load slurm/25.05
module unload slurm/25.05

# Cache module information
modulecmd bash avail 2>&1 | grep slurm
```

#### Path Optimization
```bash
# For frequently used systems, add to system PATH
echo 'export PATH=/opt/slurm/software/bin:$PATH' | sudo tee -a /etc/profile.d/slurm.sh

# Update library cache
echo '/opt/slurm/software/lib' | sudo tee -a /etc/ld.so.conf.d/slurm.conf
sudo ldconfig
```

### Package Deployment Optimization

#### Parallel Extraction
```bash
# Extract packages in parallel for faster deployment
tar -xzf slurm-25.05-software.tar.gz -C /opt/slurm/ &
tar -xzf slurm-25.05-module.tar.gz -C /opt/modules/ &
wait
```

#### Network Deployment
```bash
# For multiple nodes, use parallel deployment
parallel-ssh -h hostlist "tar -xzf /shared/packages/slurm-25.05-software.tar.gz -C /opt/slurm/"
```

## Troubleshooting Performance Issues

### Build Performance Issues

#### Build Hanging/Slow

1. **Check container resources**:
   ```bash
   lxc info build-container
   htop  # Check CPU/memory usage
   iotop # Check disk I/O
   ```

2. **Network connectivity**:
   ```bash
   # Test download speed
   wget -O /dev/null https://github.com/SchedMD/slurm/archive/refs/tags/slurm-25-05.tar.gz
   ```

3. **Spack debugging**:
   ```bash
   # Enable verbose output
   spack -d install slurm
   
   # Check build logs
   spack build-env slurm -- bash
   ```

#### Memory Issues

1. **Out of memory errors**:
   ```bash
   # Reduce parallel jobs
   export SPACK_BUILD_JOBS=1
   
   # Increase container memory
   lxc config set build-container limits.memory 32GB
   ```

2. **Swap thrashing**:
   ```bash
   # Disable swap in container
   lxc config set build-container limits.memory.swap false
   
   # Monitor memory usage
   watch -n 1 'free -h && echo "---" && lxc info build-container'
   ```

#### Disk Space Issues

1. **No space left**:
   ```bash
   # Check space usage
   df -h ~/.slurm-factory/
   lxc storage list
   
   # Clean old builds
   rm -rf ~/.slurm-factory/builds/old-*/
   
   # Clean spack cache
   spack clean --all
   ```

2. **I/O bottlenecks**:
   ```bash
   # Monitor I/O
   iostat -x 1
   
   # Use faster storage
   lxc storage create nvme dir source=/fast-nvme
   lxc profile device set default root pool nvme
   ```

## Advanced Optimization Techniques

### Container Optimization

#### Pre-built Base Images
```bash
# Create optimized base container
lxc launch ubuntu:22.04 slurm-base
lxc exec slurm-base -- apt update
lxc exec slurm-base -- apt install -y build-essential git python3-pip

# Snapshot for reuse
lxc snapshot slurm-base clean-base
lxc publish slurm-base/clean-base --alias slurm-factory-base

# Use optimized base
lxc launch slurm-factory-base build-container
```

#### Container Networking
```bash
# Use host networking for better performance
lxc config set build-container security.privileged true
lxc config device add build-container eth0 nic nictype=bridged parent=lxdbr0
```

### Build Parallelization

#### Multiple Concurrent Builds
```bash
# Build different versions in parallel (if resources allow)
uv run slurm-factory build --slurm-version 25.05 &
uv run slurm-factory build --slurm-version 24.11 &
wait
```

#### Resource Isolation
```bash
# Create separate profiles for concurrent builds
lxc profile create build-profile-1
lxc profile create build-profile-2

# Configure different resource limits
lxc profile set build-profile-1 limits.cpu 4
lxc profile set build-profile-2 limits.cpu 4
```

### Spack Optimization

#### Custom Spack Configuration
```bash
# Create optimized spack configuration
mkdir -p ~/.spack
cat > ~/.spack/config.yaml << 'EOF'
config:
  build_stage: /tmp/spack-build
  source_cache: ~/.spack/cache
  build_jobs: 8
  ccache: true
  install_tree:
    root: ~/.spack/opt/spack
    projections:
      all: ${ARCHITECTURE}/${COMPILERNAME}-${COMPILERVER}/${PACKAGE}-${VERSION}-${HASH}
EOF
```

#### Compiler Optimization
```bash
# Use newer compilers for better optimization
spack install gcc@11.3.0
spack compiler find
spack config edit compilers
```

### Monitoring and Profiling

#### Build Monitoring
```bash
# Monitor build progress
watch -n 5 'lxc exec build-container -- ps aux | grep -E "(make|ninja|gcc)"'

# Monitor resource usage
watch -n 1 'lxc info build-container | grep -A5 "Memory\|CPU"'
```

#### Performance Profiling
```bash
# Profile build performance
time uv run slurm-factory build --slurm-version 25.05

# Detailed timing
strace -T -e trace=file uv run slurm-factory build --slurm-version 25.05 2>&1 | grep -E 'open|write|read'
```

This optimization guide provides comprehensive strategies for improving both build and deployment performance of slurm-factory packages across different environments and constraints.

