#!/bin/bash

# Example of running python script in a batch mode

#SBATCH --job-name=gpujob                      # patrition name
#SBATCH --partition devel
#SBATCH --output=gpu_train_devel-job.out                 # log file
#SBATCH --time=0:45:00
#SBATCH --nodes=1
#SBATCH --gres=gpu:8
#SBATCH --ntasks-per-node=8
#SBATCH --cpus-per-task=8
#SBATCH --mem-per-cpu=32GB

# Load software
module purge

echo "Slurm job id: "${SLURM_JOB_ID}

# Run python script
python slowfast/tools/run_net.py --cfg kabr/KABR/configs/UNIFORMERv2.yaml