#!/bin/bash
#SBATCH --job-name=neighborhood_simulation    # Job name
#SBATCH --output=neighborhood_simulation_output.txt  # Standard output log
#SBATCH --error=neighborhood_simulation_error.txt    # Standard error log
#SBATCH --ntasks=1                    # Number of tasks (usually 1 for sequential jobs)
#SBATCH --cpus-per-task=10            # Number of CPU cores per task
#SBATCH --time=04:00:00               # Time limit (HH:MM:SS)
#SBATCH --mem=16G                     # Memory per node (adjust as necessary)
#SBATCH --mail-type=BEGIN,END,FAIL    # Mail events (BEGIN, END, FAIL)
#SBATCH --mail-user=zjiang402@gatech.edu    # Email address for notifications

# ========================
# LOAD MODULES AND ENVIRONMENTS
# ========================

# Load the Anaconda module
module load anaconda3

# Activate the Conda environment
source activate neighborhood_env

# ========================
# NAVIGATE TO PROJECT DIRECTORY
# ========================

# Replace the path below with the absolute path to your project directory
cd /home/hice1/mlim70/24Fa-MPONC

# ========================
# EXECUTE THE SIMULATION SCRIPT
# ========================

# Run the Python script
python main.py

