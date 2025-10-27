#!/bin/bash

#SBATCH --job-name=hud-cpu-debug
#SBATCH --account=def-zhijing
#SBATCH --partition=compute    # Using a CPU partition for faster scheduling
#SBATCH --output=/scratch/memoozd/hud-adversarial-evals/slurm_logs/slurm-cpu-%j.out
#SBATCH --error=/scratch/memoozd/hud-adversarial-evals/slurm_logs/slurm-cpu-%j.err
#SBATCH --nodes=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=00:20:00        # 20 minutes for a test run

# --- BEST PRACTICES: Fail fast and show commands ---
set -e  # Exit immediately if a command fails
set -x  # Print each command before executing it (very useful for debugging)

# --- JOB SETUP ---
echo "Job started on $(hostname) at $(date)"
echo "SLURM_JOB_ID: $SLURM_JOB_ID"

# Load required modules
module purge
module load python/3.11 apptainer

# Define paths
CODE_DIR="/project/def-zhijing/memoozd/hud-adversarial-evals"
DATA_DIR="/scratch/memoozd/hud-adversarial-evals"
VENV_DIR="${DATA_DIR}/.venv"

# Activate Python virtual environment
source "${VENV_DIR}/bin/activate"

# Export API keys from your secure file
source ~/.api_keys

# --- CRITICAL: Configure HTTP/HTTPS Proxy for Internet Access ---
echo "Configuring proxy for Alliance Canada cluster..."
export HTTP_PROXY="http://proxy.alliancecan.ca:3128"
export HTTPS_PROXY="http://proxy.alliancecan.ca:3128"

# --- RUN THE EVALUATION ---
echo "Changing to code directory: ${CODE_DIR}"
cd ${CODE_DIR}

echo "Starting HUD evaluation with Claude agent..."
# --verbose will give us more detailed logs from the hud tool itself
hud eval tasks.hpc.json \
    claude \
    --full \
    --max-concurrent ${SLURM_CPUS_PER_TASK} \
    --verbose

echo "Job finished successfully at $(date)"