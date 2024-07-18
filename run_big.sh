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
#python slowfast/tools/run_net.py --cfg kabr/KABR/configs/UNIFORMERv2_L_lr1e-4_ep50.yaml

# animal kingdom
#python slowfast/tools/run_net.py --cfg /jmain02/home/J2AD001/wwp02/mxk71-wwp02/uob_project/kabr/KABR/configs/SLOWFAST_lr3.75e-2_ep120.yaml

python slowfast/tools/run_net.py --cfg /jmain02/home/J2AD001/wwp02/mxk71-wwp02/uob_project/kabr/KABR/configs/X3D_L_lr5e-2_ep120_AK.yaml


# python slowfast/tools/run_net.py --cfg /jmain02/home/J2AD001/wwp02/mxk71-wwp02/uob_project/animal_kingdom/configs/X3D_L_lr5e-2_ep100.yaml