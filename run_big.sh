#!/bin/bash

# Example of running python script in a batch mode

#SBATCH --job-name=gpujob                      # patrition name
#SBATCH --partition big
#SBATCH --time=1-00:00:00
#SBATCH --nodes=1
#SBATCH --gres=gpu:8
#SBATCH --ntasks-per-node=8
#SBATCH --cpus-per-task=8
#SBATCH --mem-per-cpu=32GB

# Load software
module purge

echo "Slurm job id: "${SLURM_JOB_ID}


# Run python script
python slowfast/tools/run_net.py --cfg kabr/KABR/configs/UNIFORMERv2_lr2e-6_ep100.yaml