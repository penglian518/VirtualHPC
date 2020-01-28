#!/usr/bin/env python

import os
import matplotlib.pyplot as plt
import numpy as np

out_list = sorted([i for i in os.listdir('.') if i.startswith('N.')], key=lambda x: int(x.split('.')[1]))

def extract_data(outfile):
    fcon = open(outfile).readlines()

    n_tasks = [int(i.strip().split(":")[1]) for i in fcon if i.startswith('SLURM_NTASKS')][0]
    t_encry = [float(i.strip().split(":")[1]) for i in fcon if i.startswith('The encryption time is')][0]
    t_decry = [float(i.strip().split(":")[1]) for i in fcon if i.startswith('The decryption time is')][0]

    return (n_tasks, t_encry, t_decry)

# get a list of data
data = []
for outfile in out_list:
    try:
        d = extract_data(outfile)
    except:
        d = (None, None, None)

    data.append(d)

# clean the data
newdata = []
for d in data:
    if d[0]:
        if d[0] == 1:
            newdata.append((d[0], 10*d[1], 10*d[2]))
        else:
            newdata.append(d)

newdata = np.array(newdata)

# plot
fig = plt.Figure((12, 6))
ax = fig.add_subplot()
ax.plot(newdata[:, 0], newdata[0,1]/newdata[:, 1], 'o-', label='Encrypt')
ax.plot(newdata[:, 0], newdata[0,2]/newdata[:, 2], '*-', label='Decrypt')
ax.set_xticks(newdata[:, 0])
ax.set_xlabel('N cores (28 cores/socket, 56 cores/node)')
ax.set_ylabel('Times faster than 1x')
ax.set_title('Scalability of mpi4py implementation of Blowfish algorithm')
ax.legend()
fig.savefig('plot.png')

