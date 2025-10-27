
# Relocatable Deployment Guide

Complete guide for deploying **relocatable** Slurm packages built with slurm-factory to production HPC clusters with flexible installation paths using our modern CLI.

## Quick Relocatable Deployment

### 1. Build Relocatable Package

```bash
# Build CPU-optimized package (recommended for most clusters)
slurm-factory build --slurm-version 25.05

# Or build with GPU support (larger package with CUDA/ROCm)
slurm-factory build --slurm-version 25.05 --gpu

# Or minimal build (basic Slurm only, no OpenMPI)
slurm-factory build --slurm-version 25.05 --minimal

# Verbose build for troubleshooting
slurm-factory --verbose build --slurm-version 25.05
```

### 2. Locate Built Packages

Built packages are stored in your cache directory:

```bash
# List built packages
ls -la ~/.slurm-factory/builds/

# Packages for version 25.05
ls -la ~/.slurm-factory/builds/slurm-*
# slurm-25.05-software.tar.gz  (Software package: 2-25GB)
# slurm-25.05-module.tar.gz    (Module files: ~4KB)
```

### 3. Deploy to Any Location

The generated packages support **runtime path configuration** - deploy to any filesystem location:

```bash
# Option A: Standard /opt deployment
sudo mkdir -p /opt/slurm
sudo tar -xzf ~/.slurm-factory/builds/slurm-25.05-software.tar.gz -C /opt/slurm/
sudo tar -xzf ~/.slurm-factory/builds/slurm-25.05-module.tar.gz -C /usr/share/lmod/lmod/modulefiles/

# Option B: Shared filesystem deployment  
sudo mkdir -p /shared/apps/slurm-25.05
sudo tar -xzf ~/.slurm-factory/builds/slurm-25.05-software.tar.gz -C /shared/apps/slurm-25.05/
sudo tar -xzf ~/.slurm-factory/builds/slurm-25.05-module.tar.gz -C /usr/share/lmod/lmod/modulefiles/

# Option C: User-space deployment (no sudo required)
mkdir -p ~/software/slurm-25.05 ~/modules
tar -xzf ~/.slurm-factory/builds/slurm-25.05-software.tar.gz -C ~/software/slurm-25.05/
tar -xzf ~/.slurm-factory/builds/slurm-25.05-module.tar.gz -C ~/modules/
```

### 4. Configure Runtime Path

Set the installation path at module load time:

```bash
# For standard /opt deployment (uses default built-in path)
module load slurm/25.05

# For custom location (override with environment variable)
export SLURM_INSTALL_PREFIX=/shared/apps/slurm-25.05/software
module load slurm/25.05

# For user-space deployment
export MODULEPATH=$HOME/modules:$MODULEPATH
export SLURM_INSTALL_PREFIX=$HOME/software/slurm-25.05/software  
module load slurm/25.05
```

### 4. Verify Relocatable Installation

```bash
# Check that paths point to your custom location
which srun squeue sinfo        # Should show custom path
echo $SLURM_ROOT              # Should show: /your/custom/path
echo $SLURM_PREFIX            # Should show: /your/custom/path

# Verify functionality
slurmd --version
sinfo --help
```

## Package Structure & Contents

### Software Package (`slurm-25.05-software.tar.gz`)

**Size**: ~2-5GB (CPU) / ~15-25GB (GPU) / ~1-2GB (minimal)

**Relocatable Structure**:
```
software/                    # Relocatable root directory
├── bin/                     # Slurm executables  
│   ├── srun, sbatch, squeue # Job management commands
│   ├── sinfo, scontrol      # Cluster management
│   └── sacct, sreport       # Accounting tools
├── sbin/                    # System daemons
│   ├── slurmd              # Compute node daemon
│   ├── slurmctld           # Controller daemon  
│   ├── slurmdbd            # Database daemon
│   └── slurmrestd          # REST API daemon
├── lib/                     # Runtime libraries
│   ├── libslurm.so*        # Core Slurm library
│   ├── slurm/              # Plugin libraries
│   │   ├── accounting_storage_*.so
│   │   ├── job_submit_*.so
│   │   ├── select_*.so
│   │   └── task_*.so
│   └── dependencies/        # Bundled runtime deps
│       ├── libmunge.so*    # Authentication
│       ├── libjson-c.so*   # JSON parsing
│       ├── libcurl.so*     # HTTP client
│       └── libssl.so*      # SSL/TLS
├── include/                 # Development headers
│   └── slurm/
├── share/                   # Documentation & configs
│   ├── man/                # Manual pages
│   ├── doc/                # Documentation
│   └── slurm/              # Example configs
└── etc/                     # Configuration templates
    └── slurm.conf.example
```

### Module Package (`slurm-25.05-module.tar.gz`)

**Size**: ~4KB

**Relocatable Module Structure**:
```
modules/
└── slurm/
    └── 25.05.lua           # Dynamic Lmod module

# Alternative hierarchy support  
modulefiles/
└── slurm/
    └── 25.05               # Traditional module format
```

**Module Features**:
- **Dynamic Prefix**: `${SLURM_INSTALL_PREFIX:-{prefix}}` substitution
- **Build Metadata**: Version, type, GPU support indicators
- **Conflict Management**: Prevents loading multiple Slurm versions
- **Help Integration**: Usage instructions and path customization help
- **Environment Setup**: Comprehensive PATH, LD_LIBRARY_PATH configuration

**Module automatically configures**:
- `PATH` - Adds `/opt/slurm/software/bin` and `/opt/slurm/software/sbin`
- `LD_LIBRARY_PATH` - Adds `/opt/slurm/software/lib` and `/opt/slurm/software/lib/slurm`
- `MANPATH` - Adds `/opt/slurm/software/share/man`
- `PKG_CONFIG_PATH` - Adds `/opt/slurm/software/lib/pkgconfig`
- `SLURM_ROOT` - Set to `/opt/slurm/software`
- `SLURM_CONF` - Default to `/etc/slurm/slurm.conf`

## Module Usage

```bash
# Load the module
module load slurm/25.05

# Check what was loaded
module list

# Test basic functionality
srun --help | head -5
slurmd --version

# Unload when done
module unload slurm/25.05
```

## Advanced Deployment Scenarios

### Multi-Version Deployment

Deploy multiple Slurm versions side-by-side:

```bash
# Build different versions
uv run slurm-factory build --slurm-version 25.05
uv run slurm-factory build --slurm-version 24.11

# Deploy both versions
sudo tar -xzf ~/.slurm-factory/builds/25.05/slurm-25.05-software.tar.gz -C /opt/slurm/
sudo tar -xzf ~/.slurm-factory/builds/24.11/slurm-24.11-software.tar.gz -C /opt/slurm/
sudo tar -xzf ~/.slurm-factory/builds/25.05/slurm-25.05-module.tar.gz -C /opt/modules/
sudo tar -xzf ~/.slurm-factory/builds/24.11/slurm-24.11-module.tar.gz -C /opt/modules/

# Users can choose versions
module avail slurm
module load slurm/25.05  # or slurm/24.11
```

### Shared Filesystem Deployment

For clusters with shared filesystems (NFS, Lustre, etc.):

```bash
# Deploy to shared location
sudo mkdir -p /shared/software/slurm /shared/modules
sudo tar -xzf ~/.slurm-factory/builds/25.05/slurm-25.05-software.tar.gz -C /shared/software/slurm/
sudo tar -xzf ~/.slurm-factory/builds/25.05/slurm-25.05-module.tar.gz -C /shared/modules/

# Configure on all nodes
echo 'export MODULEPATH=/shared/modules:$MODULEPATH' | sudo tee -a /etc/profile.d/modules.sh
```

### Container Deployment

For containerized environments:

```bash
# Extract to container build context
mkdir -p container-build/opt/slurm container-build/opt/modules
tar -xzf ~/.slurm-factory/builds/25.05/slurm-25.05-software.tar.gz -C container-build/opt/slurm/
tar -xzf ~/.slurm-factory/builds/25.05/slurm-25.05-module.tar.gz -C container-build/opt/modules/

# Add to Dockerfile
cat >> Dockerfile << 'EOF'
COPY container-build/opt/slurm /opt/slurm/
COPY container-build/opt/modules /opt/modules/
ENV MODULEPATH=/opt/modules:$MODULEPATH
EOF
```

## Setting up Slurm Cluster

After deploying the packages, configure Slurm for your cluster:

### 1. Create Slurm Configuration

```bash
# Load the module
module load slurm/25.05

# Create configuration directory
sudo mkdir -p /etc/slurm

# Generate basic configuration
sudo tee /etc/slurm/slurm.conf << 'EOF'
ClusterName=cluster
ControlMachine=controller
SlurmUser=slurm
SlurmctldPort=6817
SlurmdPort=6818
AuthType=auth/munge
CryptoType=crypto/munge
StateSaveLocation=/var/spool/slurm/ctld
SlurmdSpoolDir=/var/spool/slurm/d
SwitchType=switch/none
MpiDefault=none
ProctrackType=proctrack/pgid
TaskPlugin=task/none
ReturnToService=2
SlurmctldPidFile=/var/run/slurmctld.pid
SlurmdPidFile=/var/run/slurmd.pid
SlurmctldLogFile=/var/log/slurm/slurmctld.log
SlurmdLogFile=/var/log/slurm/slurmd.log

# Node configuration (customize for your cluster)
NodeName=node[01-04] CPUs=8 Sockets=1 CoresPerSocket=8 ThreadsPerCore=1 RealMemory=32000 State=UNKNOWN
PartitionName=compute Nodes=node[01-04] Default=YES MaxTime=INFINITE State=UP
EOF
```

### 2. Create Slurm User and Directories

```bash
# Create slurm user
sudo useradd --system --shell /bin/false slurm

# Create directories
sudo mkdir -p /var/spool/slurm/{ctld,d} /var/log/slurm
sudo chown -R slurm:slurm /var/spool/slurm /var/log/slurm
```

### 3. Start Slurm Daemons

```bash
# On controller node
sudo slurmctld -D

# On compute nodes  
sudo slurmd -D

# Or create systemd services (recommended)
```

### 4. Test Job Submission

```bash
# Test basic functionality
sinfo                    # Show cluster state
srun --pty bash         # Interactive job
sbatch script.sh        # Batch job
squeue                  # Show job queue
```

## Production Deployment Best Practices

### Security Considerations

1. **File Permissions**:
```bash
# Restrict access to Slurm binaries
sudo chmod 755 /opt/slurm/software/bin/*
sudo chmod 755 /opt/slurm/software/sbin/*

# Protect configuration
sudo chmod 644 /etc/slurm/slurm.conf
sudo chown root:root /etc/slurm/slurm.conf
```

2. **Network Security**:
- Use firewalls to restrict Slurm port access
- Consider VPN for cluster communication
- Implement proper authentication (Munge)

3. **User Access**:
```bash
# Create slurm group for users
sudo groupadd slurm-users
sudo usermod -a -G slurm-users username
```

### Performance Optimization

1. **Module Loading**:
```bash
# Add to user shell startup for automatic loading
echo 'module load slurm/25.05' >> ~/.bashrc
```

2. **Path Optimization**:
```bash
# For frequently used systems, add to system PATH
echo 'export PATH=/opt/slurm/software/bin:$PATH' | sudo tee -a /etc/profile.d/slurm.sh
```

3. **Library Caching**:
```bash
# Update library cache
echo '/opt/slurm/software/lib' | sudo tee -a /etc/ld.so.conf.d/slurm.conf
sudo ldconfig
```

### Monitoring and Maintenance

1. **Health Checks**:
```bash
# Regular health check script
#!/bin/bash
module load slurm/25.05
if ! sinfo &>/dev/null; then
    echo "ERROR: Slurm controller not responding"
    exit 1
fi
echo "Slurm cluster healthy"
```

2. **Log Rotation**:
```bash
# Configure logrotate for Slurm logs
sudo tee /etc/logrotate.d/slurm << 'EOF'
/var/log/slurm/*.log {
    daily
    missingok
    rotate 52
    compress
    notifempty
    create 640 slurm slurm
    postrotate
        /bin/kill -HUP `cat /var/run/slurmctld.pid 2> /dev/null` 2> /dev/null || true
    endscript
}
EOF
```

## Troubleshooting Deployment

### Module Issues

**Module not found**:
```bash
# Check module path
echo $MODULEPATH
module avail

# Verify module file exists
ls -la /opt/modules/slurm/
```

**Module loads but commands not found**:
```bash
# Check module configuration
module show slurm/25.05

# Verify PATH setting
echo $PATH | grep slurm
```

### Library Issues

**Library errors when running Slurm commands**:
```bash
# Check library path
echo $LD_LIBRARY_PATH | grep slurm

# Test library loading
ldd $(which srun)

# Manual library path (if needed)
export LD_LIBRARY_PATH=/opt/slurm/software/lib:$LD_LIBRARY_PATH
```

### Permission Issues

**Permission denied errors**:
```bash
# Check file permissions
ls -la /opt/slurm/software/bin/srun

# Fix permissions if needed
sudo chmod 755 /opt/slurm/software/bin/*
sudo chmod 755 /opt/slurm/software/sbin/*
```

### Configuration Issues

**Slurm commands complain about missing configuration**:
```bash
# Check configuration file
ls -la /etc/slurm/slurm.conf

# Test configuration
slurmctld -t  # Test controller config
slurmd -t     # Test compute node config
```

## Files and Directories Reference

```
/opt/slurm/
├── software/                    # Slurm binaries and libraries
│   ├── bin/                    # User commands (srun, sbatch, etc.)
│   ├── sbin/                   # Administrative commands (slurmd, slurmctld, etc.)
│   ├── lib/                    # Shared libraries
│   ├── include/                # Development headers  
│   └── share/                  # Documentation and data
/opt/modules/
└── slurm/                      # Module files
    ├── 25.05.lua              # Slurm 25.05 module
    └── 24.11.lua              # Slurm 24.11 module
/etc/slurm/
├── slurm.conf                 # Main configuration file
├── slurmdbd.conf              # Database configuration
└── gres.conf                  # Generic resource configuration
/var/spool/slurm/
├── ctld/                      # Controller state files
└── d/                         # Compute node state files
/var/log/slurm/
├── slurmctld.log             # Controller logs
├── slurmd.log                # Compute node logs
└── slurmdbd.log              # Database logs
```

