#!/usr/bin/env python
import filecmp, os
from blowfish import FileEncrypt


fn = FileEncrypt()
fn.key = '1234 abcd 4321 dcba'

f_org = 'kjv-bible.txt'
f_encrypted = 'test_encrypted.txt'
f_decrypted = 'test_decrypted.txt'

try:
    os.remove(f_encrypted)
    os.remove(f_decrypted)
except:
    print("Failed to cleanup the files")


print('The key used for encryption and decryption is:', fn.key)
print('Starts to encrypt ...')
fn.Encrypt(f_org, f_encrypted)

print('Starts to decrypt ...')
fn.Decrypt(f_encrypted, f_decrypted)

if filecmp.cmp(f_org, f_decrypted):
    print('\nGood Job. %s and %s have no differences.\n' % (f_org, f_decrypted))
