#!/bin/bash
#SBATCH --job-name=MPI                                              # job name
#SBATCH --partition=256GBv1                                           # select partion from 128GB, 256GB, 384GB, GPU and super
#SBATCH --nodes=2                                                # number of nodes requested by user
#SBATCH --ntasks-per-node=56                                                 # number of tasks per node
#SBATCH --gres=gpu:0                                     # use generic resource GPU, format: --gres=gpu:[n], n is the number of GPU card
#SBATCH --time=0-01:00:00                                           # run time, format: D-H:M:S (max wallclock time)
#SBATCH --output=N.112.%j.out                                         # redirect both standard output and erro output to the same file

# load module
module load python/3.7.x-anaconda
# start the virtual environment
source activate py3

echo "SLURM_NTASKS: $SLURM_NTASKS"

mpirun -np $SLURM_NTASKS python blowfish_mpi.py

