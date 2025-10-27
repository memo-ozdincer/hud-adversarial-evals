#!/bin/bash

#SBATCH --job-name=hud-adversarial-evals
#SBATCH --account=def-zhijing

# --- TRILIUM FIXES ---
# 1. Specify the mandatory partition for whole-node jobs.
#SBATCH --partition=compute_full_node

# 2. Explicitly request all 4 GPUs on the node, as required by this partition.
#    Your code will run on the CPU, but SLURM needs this to allocate the node.
#SBATCH --gpus-per-node=4

# 3. Removed the --mem=16G line, as it's not allowed on Trillium.

# --- PATHS AND RESOURCES ---
# Your output paths are already correct, pointing to scratch space.
#SBATCH --output=/scratch/memoozd/hud-adversarial-evals/slurm_logs/slurm-%j.out
#SBATCH --error=/scratch/memoozd/hud-adversarial-evals/slurm_logs/slurm-%j.err

# Resource requests that are still valid
#SBATCH --nodes=1
#SBATCH --cpus-per-task=8      # Requesting 8 CPUs is fine
#SBATCH --time=00:30:00      # 30-minute time limit

# --- JOB SETUP ---
echo "Job started on $(hostname) at $(date)"
echo "Running on Trillium cluster in partition: $SLURM_JOB_PARTITION"

# Load the same modules you used for setup
module purge
module load python/3.11 apptainer

# Define project paths
CODE_DIR="/project/def-zhijing/memoozd/hud-adversarial-evals"
DATA_DIR="/scratch/memoozd/hud-adversarial-evals"
VENV_DIR="${DATA_DIR}/.venv"
LOG_DIR="${DATA_DIR}/slurm_logs"

# Create log directory if it doesn't exist (good practice)
mkdir -p ${LOG_DIR}

# Activate the virtual environment
echo "Activating virtual environment from: ${VENV_DIR}"
source "${VENV_DIR}/bin/activate"

# Export API keys and Apptainer credentials
echo "Loading API keys and credentials..."
source ~/.api_keys 
export APPTAINER_DOCKER_USERNAME="memo-ozdincer"
export APPTAINER_DOCKER_PASSWORD="${GITHUB_PAT}" # GITHUB_PAT comes from .api_keys

# --- RUN THE EVALUATION ---
echo "Starting HUD evaluation script..."
cd ${CODE_DIR}

# This command is well-formed and should work correctly now.
hud eval tasks.hpc.json \
    claude \
    --full \
    --max-concurrent ${SLURM_CPUS_PER_TASK}

echo "Job finished at $(date)"