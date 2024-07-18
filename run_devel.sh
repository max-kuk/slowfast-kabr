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
#python slowfast/tools/run_net.py --cfg kabr/KABR/configs/SLOWFAST.yaml


# animal kingdom
python slowfast/tools/run_net.py --cfg /jmain02/home/J2AD001/wwp02/mxk71-wwp02/uob_project/kabr/KABR/configs/SLOWFAST_lr3.75e-2_ep120-best_epoch.yaml