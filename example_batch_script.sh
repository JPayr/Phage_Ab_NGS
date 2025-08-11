#!/bin/bash

#SBATCH --job-name=antibody_NG
#SBATCH --output=antibody_NGS.out
#SBATCH --gpus=4
#SBATCH --time=24:00:00         # Hours:Mins:Secs

hostname
nvidia-smi --list-gpus

source ~/miniforge3/bin/activate boltz

date

boltz predict /home/u5x/johnpaul.u5x/boltz/NGS_clone_Gen/ --recycling_steps 10 --diffusion_samples 50 --devices 4 --use_msa_server --out_dir /home/u5x/johnpaul.u5x/boltz/calprotectin/

date
