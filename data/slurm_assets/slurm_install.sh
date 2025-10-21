#!/bin/bash
# Slurm Installation and Configuration Script
# This script sets up the Slurm workload manager filesystem and configuration

set -euo pipefail

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=== Slurm Installation Script ==="
echo "This script will:"
echo "  1. Create necessary directories"
echo "  2. Install configuration files"
echo "  3. Install systemd service files"
echo "  4. Set up proper permissions"
echo "  5. Download and install Slurm software"
echo

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo "Error: This script must be run as root" 
   exit 1
fi

# Check if slurm user exists
if ! id slurm &>/dev/null; then
    echo "Error: slurm user does not exist. Please create it first:"
    echo "  useradd --system --uid 64031 --no-create-home --shell /usr/sbin/nologin slurm"
    exit 1
fi

# Check if slurmrestd user exists
if ! id slurmrestd &>/dev/null; then
    echo "Error: slurmrestd user does not exist. Please create it first:"
    echo "  useradd --system --uid 64032 --no-create-home --shell /usr/sbin/nologin slurmrestd"
    exit 1
fi

echo "=== Creating Slurm directories ==="
mkdir -p /etc/slurm
mkdir -p /opt/slurm
mkdir -p /var/lib/slurm
mkdir -p /var/lib/slurm/checkpoint
mkdir -p /var/lib/slurm/slurmd
mkdir -p /var/lib/slurm/slurmctld
mkdir -p /var/log/slurm
mkdir -p /var/spool/slurmd

echo "=== Installing Slurm configuration files ==="
install -m 0644 -o root -g root "${SCRIPT_DIR}/slurm/oci.conf" /etc/slurm/oci.conf
install -m 0644 -o root -g root "${SCRIPT_DIR}/slurm/cgroup.conf" /etc/slurm/cgroup.conf
install -m 0644 -o root -g root "${SCRIPT_DIR}/slurm/slurm.conf" /etc/slurm/slurm.conf
install -m 0600 -o root -g root "${SCRIPT_DIR}/slurm/slurmdbd.conf" /etc/slurm/slurmdbd.conf
install -m 0644 -o root -g root "${SCRIPT_DIR}/slurm/acct_gather.conf" /etc/slurm/acct_gather.conf

echo "=== Installing systemd service files ==="
install -m 0644 -o root -g root "${SCRIPT_DIR}/systemd/slurmctld.service" /usr/lib/systemd/system/slurmctld.service
install -m 0644 -o root -g root "${SCRIPT_DIR}/systemd/slurmd.service" /usr/lib/systemd/system/slurmd.service
install -m 0644 -o root -g root "${SCRIPT_DIR}/systemd/slurmdbd.service" /usr/lib/systemd/system/slurmdbd.service
install -m 0644 -o root -g root "${SCRIPT_DIR}/systemd/slurmrestd.service" /usr/lib/systemd/system/slurmrestd.service

echo "=== Installing default environment files ==="
mkdir -p /etc/default
install -m 0644 -o root -g root "${SCRIPT_DIR}/defaults/slurmd" /etc/default/slurmd
install -m 0644 -o root -g root "${SCRIPT_DIR}/defaults/slurmctld" /etc/default/slurmctld
install -m 0644 -o root -g root "${SCRIPT_DIR}/defaults/slurmdbd" /etc/default/slurmdbd
install -m 0644 -o root -g root "${SCRIPT_DIR}/defaults/slurmrestd" /etc/default/slurmrestd

echo "=== Installing tmpfiles.d configuration ==="
mkdir -p /etc/tmpfiles.d
install -m 0644 -o root -g root "${SCRIPT_DIR}/tmpfiles.d/slurmctld.conf" /etc/tmpfiles.d/slurmctld.conf
install -m 0644 -o root -g root "${SCRIPT_DIR}/tmpfiles.d/slurmd.conf" /etc/tmpfiles.d/slurmd.conf
install -m 0644 -o root -g root "${SCRIPT_DIR}/tmpfiles.d/slurmdbd.conf" /etc/tmpfiles.d/slurmdbd.conf
install -m 0644 -o root -g root "${SCRIPT_DIR}/tmpfiles.d/slurmrestd.conf" /etc/tmpfiles.d/slurmrestd.conf

echo "=== Installing profile.d script for Lmod ==="
mkdir -p /etc/profile.d
install -m 0644 -o root -g root "${SCRIPT_DIR}/profile.d/z00_lmod.sh" /etc/profile.d/z00_lmod.sh

echo "=== Generating Slurm authentication key ==="
if [[ ! -f /etc/slurm/slurm.key ]]; then
    openssl rand 2048 | base64 | tr -d '\n' > /etc/slurm/slurm.key
    chmod 600 /etc/slurm/slurm.key
    chown slurm:slurm /etc/slurm/slurm.key
    echo "Generated new slurm.key"
else
    echo "slurm.key already exists, skipping"
fi

echo "=== Setting Slurm directory permissions ==="
chown -R slurm:slurm /var/log/slurm
chown -R slurm:slurm /var/lib/slurm
chown slurm:slurm /etc/slurm/slurmdbd.conf
chown slurm:slurm /etc/slurm/slurm.conf

echo "=== Downloading and installing Slurm Lmod module ==="
if [[ -d /usr/share/lmod/lmod/modulefiles ]]; then
    wget -qO- https://vantage-public-assets.s3.us-west-2.amazonaws.com/slurm/25.05/slurm-module-latest.tar.gz | \
        tar --no-same-owner --no-same-permissions --touch -xz -C /usr/share/lmod/lmod/modulefiles
    echo "Slurm Lmod module installed"
else
    echo "Warning: Lmod modulefiles directory not found, skipping module installation"
fi

echo "=== Downloading and installing Slurm software ==="
wget -qO- https://vantage-public-assets.s3.us-west-2.amazonaws.com/slurm/25.05/slurm-latest.tar.gz | \
    tar --no-same-owner --no-same-permissions --touch -xz -C /opt/slurm
echo "Slurm software installed to /opt/slurm"

echo "=== Creating Slurm command wrapper scripts ==="
for i in /opt/slurm/software/bin/sacct \
  /opt/slurm/software/bin/sacctmgr \
  /opt/slurm/software/bin/salloc \
  /opt/slurm/software/bin/sattach \
  /opt/slurm/software/bin/sbang \
  /opt/slurm/software/bin/sbatch \
  /opt/slurm/software/bin/sbcast \
  /opt/slurm/software/bin/scancel \
  /opt/slurm/software/bin/scontrol \
  /opt/slurm/software/bin/scrontab \
  /opt/slurm/software/bin/sdiag \
  /opt/slurm/software/bin/sh5util \
  /opt/slurm/software/bin/sinfo \
  /opt/slurm/software/bin/sprio \
  /opt/slurm/software/bin/squeue \
  /opt/slurm/software/bin/sreport \
  /opt/slurm/software/bin/srun \
  /opt/slurm/software/bin/sshare \
  /opt/slurm/software/bin/sstat \
  /opt/slurm/software/bin/strigger \
  /opt/slurm/software/sbin/slurmctld \
  /opt/slurm/software/sbin/slurmd \
  /opt/slurm/software/sbin/slurmdbd \
  /opt/slurm/software/sbin/slurmrestd \
  /opt/slurm/software/sbin/slurmstepd; do

  if [[ ! -f "$i" ]]; then
    echo "Warning: $i not found, skipping wrapper creation"
    continue
  fi

  BASENAME=$(basename "$i")
  
  case "$i" in
    *sbin*)
      TARGET_DIR="/usr/sbin"
      ;;
    *)
      TARGET_DIR="/usr/bin"
      ;;
  esac
  
  echo "Creating wrapper for $BASENAME in $TARGET_DIR"
  
  # Create wrapper script that sources z00_lmod.sh (which loads slurm module) before executing
  cat > "${TARGET_DIR}/${BASENAME}" << WRAPPER_EOF
#!/bin/bash
source /etc/profile.d/z00_lmod.sh
exec $i "\$@"
WRAPPER_EOF
  
  # Make wrapper executable
  chmod +x "${TARGET_DIR}/${BASENAME}"

done

echo "=== Creating runtime directories ==="
systemd-tmpfiles --create /etc/tmpfiles.d/slurmctld.conf
systemd-tmpfiles --create /etc/tmpfiles.d/slurmd.conf
systemd-tmpfiles --create /etc/tmpfiles.d/slurmdbd.conf
systemd-tmpfiles --create /etc/tmpfiles.d/slurmrestd.conf

echo "=== Reloading systemd daemon ==="
systemctl daemon-reload

echo
echo "=== Slurm installation complete! ==="
echo
echo "Next steps:"
echo "  1. Edit /etc/slurm/slurm.conf to replace @VARIABLES@ with actual values:"
echo "     - @CLUSTER_NAME@"
echo "     - @HEADNODE_HOSTNAME@"
echo "     - @HEADNODE_ADDRESS@"
echo "     - @CPUs@, @THREADS_PER_CORE@, @CORES_PER_SOCKET@, @SOCKETS@, @REAL_MEMORY@"
echo
echo "  2. Edit /etc/slurm/slurmdbd.conf to replace @HEADNODE_HOSTNAME@"
echo
echo "  3. Ensure MySQL is configured and the slurm database exists"
echo
echo "  4. Enable and start Slurm services:"
echo "     systemctl enable --now slurmdbd"
echo "     systemctl enable --now slurmctld"
echo "     systemctl enable --now slurmd"
echo
echo "  5. Verify services are running:"
echo "     systemctl status slurmdbd slurmctld slurmd"
echo
