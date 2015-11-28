#!/usr/bin/env python

"""
Python Program/Script that enables encryption and decryption of files and directories
It only runs on linux, deal with it

@author Hermann Krumrey <hermann@krumreyh.com>
"""

#imports
import os
import sys
import argparse
from sys import platform as _platform

#platform check
if not _platform == "linux":
    print("This program only works on Linux!")
    sys.exit(1)

# hardcoded variables
keyFile = os.getenv("HOME") + "/.ssh/key.bin"
paranoidKeyFile = os.getenv("HOME") + "/.ssh/key2.bin"

# argument parser
parser = argparse.ArgumentParser()
parser.add_argument("file_to_encrypt", help="the file or directory to encrypt")
parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
parser.add_argument("-k", "--key", help="Specify a custom key", dest="key1", action="store_true")
parser.add_argument("-p", "--paranoidKey", help="Specify a custom key key for zip files", dest="key2", action="store_true")
parser.add_argument("-z", "--zipped", help="zips the files and encrypts the zipped file using a different key.", action="store_true")
parser.add_argument("-t", "--trash", help="deletes the original file/directory", action="store_true")
parser.add_argument("-d", "--decrypt", help="decrypts all encrypted files in a directory or zip file", action="store_true")
args = parser.parse_args()

#check for valid pathname
if not os.path.isfile(args.file_to_encrypt) or args.file_to_encrypt.endswith("/"):
    print("File not found")
    sys.exit(1)
if args.decrypt and not args.file_to_encrypt.endswith(".enc"):
    if not os.path.isdir(args.file_to_encrypt):
        print("Not a valid file to decrypt")
        sys.exit(1)

#determining mission parameters
isFile = False
isDir = False

if os.path.isdir(args.file_to_encrypt):
    isDir = True
else:
    isFile = True

# functions
"""
Encrypts a single file and deletes the original file if specified
@param file - the file to encrypt
@param deleteOld - specify True if the original should be deleted
"""
def encryptFile(file, deleteOld):
    if args.verbose: print("encrypting file " + file)
    os.system("openssl enc -aes-256-cbc -salt -in \"" + file + "\" -out \"" + file + ".enc\" -pass file:" + keyFile)
    if args.verbose: print("created encrypted file " + file + ".enc")
    if deleteOld:
        if args.verbose: print("Deleting file " + file)
        os.system("rm " + file)


"""
Decrypts a single encrypted and deletes the original encrypted file if specified
@param file - the file to be decrypted
@param deleteOld - specify True if the original encrypted file should be deleted
"""
def decryptfile(file, deleteOld):
    newFile = file.split(".enc")[0]
    if args.verbose: print("decrypting file")
    os.system("openssl enc -d -aes-256-cbc -in \"" + file + "\" -out \"" + newFile + "\" -pass file:" + keyFile)
    if args.verbose: print("created decrypted file " + newFile)
    if deleteOld:
        if args.verbose: print("deleting encrypted file")
        os.system("rm " + file)

"""
Encrypts an entire directory
@param directory - the directory to be encrypted
@param deleteOld - specify True, if the original directory should be deleted
@param createCopy - always specify true, this is used as a helper variable in recursion
"""
def encryptDirectory(directory, deleteOld, createCopy):
    if createCopy:
        if args.verbose: print("creating copy of directory")
        os.system("cp -ar " + directory + " " + directory + "_encrypted")
    directoryContent = os.listdir(directory + "_encrypted")
    for child in directoryContent:
        childPath = directory + "/" + child
        if args.verbose: print("Checking if " + childPath + " is a directory")
        if os.path.isdir(childPath):
            encryptDirectory(childPath, False, False)
        else:
            encryptFile(childPath, True)
    if deleteOld and deleteOld:
        if args.verbose: print("Deleting original directory")
        os.system("rm -rf " + directory + "/")

def decryptDirectory(directory, deleteOld):
    print("TODO")

"""
Zips a directory
@param directory - the directory to be zipped
"""
def zipDirectory(directory):
    if args.verbose: print("Zipping Directory " + directory)
    os.system("zip -r " + directory + ".zip " + os.path.dirname(directory))
    if args.verbose: print("Deleting Directory " + directory)
    os.system("rm -rf " + directory)

"""
Zips a file
@param file - the file to be zipped
"""
def zipFile(file):
    if args.verbose: print("Zipping File " + file)
    os.system("zip " + file + ".zip " + file)
    if args.verbose: print("Deleting File " + file)
    os.system("rm " + file)

"""
Encrypts a zip file with a different key
@param zipfile - the zip file to be encrypted
"""
def encryptZipFile(zipfile):
    if args.verbose: print("encrypting zip file " + zipfile)
    os.system("openssl enc -aes-256-cbc -salt -in \"" + zipfile + "\" -out \"" + zipfile + ".enc\" -pass file:" + paranoidKeyFile)
    if args.verbose: print("created encrypted file " + zipfile + ".enc")
    if args.verbose: print("Deleting zip file " + zipfile)
    os.system("rm " + zipfile)

#main routine

if not args.decrypt:
    if args.zipped:
        if args.trash:
            if os.path.isdir(args.file_to_encrypt):
                encryptDirectory(args.file_to_encrypt, True, True)
                zipDirectory(args.path_to_encrypt + "_encrypted")
            else:
                encryptFile(args.file_to_encrypt, True)
                zipFile(args.file_to_encrypt + ".enc")
        else:
            if os.path.isdir(args.file_to_encrypt):
                encryptDirectory(args.file_to_encrypt, False, True)
                zipDirectory(args.path_to_encrypt + "_encrypted")
            else:
                encryptFile(args.file_to_encrypt, False)
                zipFile(args.file_to_encrypt + ".enc")
    else:
        if args.trash:
            if os.path.isdir(args.file_to_encrypt):
                encryptDirectory(args.file_to_encrypt, True, True)
            else:
                encryptFile(args.file_to_encrypt, True)
        else:
            if os.path.isdir(args.file_to_encrypt):
                encryptDirectory(args.file_to_encrypt, False, True)
            else:
                encryptFile(args.file_to_encrypt, False)
else:
    if args.trash:
        if os.path.isdir(args.file_to_encrypt):
            decryptDirectory(args.file_to_encrypt, True)
        else:
            decryptfile(args.file_to_encrypt, True)
    else:
        if os.path.isdir(args.file_to_encrypt):
            decryptDirectory(args.file_to_encrypt, False)
        else:
            decryptfile(args.file_to_encrypt, False)