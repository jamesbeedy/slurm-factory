. /usr/share/lmod/lmod/init/profile
module use /opt/slurm/software/assets/modules
export SLURM_INSTALL_PREFIX=/opt/slurm/software
# Load the slurm module (find it dynamically since hash changes)
SLURM_MODULE=$(ls /opt/slurm/software/assets/modules/slurm/*.lua 2>/dev/null | head -1 | xargs basename -s .lua)
if [ -n "$SLURM_MODULE" ]; then
    module load slurm/"$SLURM_MODULE"
fi
