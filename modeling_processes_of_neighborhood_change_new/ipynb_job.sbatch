#!/bin/bash
#SBATCH --job-name=ipynb_job    # Job name
#SBATCH --output=ipynb_job.txt  # Output file (stdout)
#SBATCH --error=factorial_error.txt   # Error file (stderr)
#SBATCH --ntasks=1                    # Number of tasks (usually 1 for a sequential job)
#SBATCH --cpus-per-task=10            # Number of CPU cores
#SBATCH --time=01:00:00               # Time limit (HH:MM:SS)
#SBATCH --mem=2G                      # Memory per node (adjust as necessary)
#SBATCH --mail-type=BEGIN,END,FAIL    # Mail Preference
#SBATCH --mail-user=mlim70@gatech.edu    # Email for notification
 
# Load the necessary modules for Python
 
# Execute your Python script
python main.ipynb
 
##type "sbatch myjob.sbatch" into command line to execute this file
##type "squeue -u your_username" into command line to check on status
 
