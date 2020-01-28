#!/usr/bin/env python
import filecmp, os
from blowfish import pFileEncrypt

from mpi4py import MPI

comm = MPI.COMM_WORLD
rank = comm.Get_rank()  # id of processor

fn = pFileEncrypt()
fn.key = '1234 abcd 4321 dcba'

f_org = 'bible.txt'
f_encrypted = 'test_encrypted.txt'
f_decrypted = 'test_decrypted.txt'

# clean up the files
if rank == 0:
    try:
        os.remove(f_encrypted)
        os.remove(f_decrypted)
    except:
        print("Failed to cleanup the files")

if rank == 0:
    print('Starts to encrypt ...')

fn.Encrypt(f_org, f_encrypted)

if rank == 0:
    print('Starts to decrypt ...')

fn.Decrypt(f_encrypted, f_decrypted)

if rank == 0:
    if filecmp.cmp(f_org, f_decrypted):
        print('\nGood Job. %s and %s have no differences.\n' % (f_org, f_decrypted))
