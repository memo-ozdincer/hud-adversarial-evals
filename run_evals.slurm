#!/bin/bash

#SBATCH --job-name=hud-adversarial-evals
#SBATCH --account=def-zhijing
#SBATCH --output=/scratch/memoozd/hud-adversarial-evals/slurm_logs/slurm-%j.out
#SBATCH --error=/scratch/memoozd/hud-adversarial-evals/slurm_logs/slurm-%j.err
#SBATCH --nodes=1
#SBATCH --cpus-per-task=4         # Start with a smaller number for simple tasks
#SBATCH --mem=16G                 # 16GB memory should be plenty
#SBATCH --time=00:30:00           # 30 minutes is enough for initial tests

# --- JOB SETUP ---
echo "Job started on $(hostname) at $(date)"

# Load the same modules you used for setup
module purge
module load python/3.11 apptainer

# Define project paths
CODE_DIR="/project/def-zhijing/memoozd/hud-adversarial-evals"
DATA_DIR="/scratch/memoozd/hud-adversarial-evals"
VENV_DIR="${DATA_DIR}/.venv"
LOG_DIR="${DATA_DIR}/slurm_logs"

# Create log directory if it doesn't exist
mkdir -p ${LOG_DIR}

# Activate the virtual environment
source "${VENV_DIR}/bin/activate"

# Export API keys (assuming you have a file with export statements)
# IMPORTANT: Make sure this file is secure and not tracked by git
source ~/.api_keys 

# --- RUN THE EVALUATION ---
echo "Starting HUD evaluation script..."
cd ${CODE_DIR}

# Run the evaluation using the HPC-specific task file
# We'll run the full dataset with concurrency matching the number of CPUs
hud eval tasks.hpc.json \
    claude \
    --full \
    --max-concurrent ${SLURM_CPUS_PER_TASK}

echo "Job finished at $(date)"