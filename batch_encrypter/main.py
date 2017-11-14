#!/usr/bin/env python
"""
Copyright 2015-2017 Hermann Krumrey <hermann@krumreyh.com>

This file is part of batch-encrypter.

batch-encrypter is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

batch-encrypter is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with batch-encrypter.  If not, see <http://www.gnu.org/licenses/>.
"""

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
homedir = os.getenv("HOME")
progdir = homedir + "/.batch-encrypt"
keyFile = progdir + "/key1.bin"
paranoidKeyFile = progdir + "/key2.bin"

#install check
installed = False
if os.path.isfile(keyFile) or os.path.isfile(paranoidKeyFile):
    installed = True

# argument parser
parser = argparse.ArgumentParser()
if installed:
    parser.add_argument("file_to_encrypt", help="the file or directory to encrypt")
    parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
    parser.add_argument("-k", "--key", help="Specify a custom key", dest="key1", action="store_true")
    parser.add_argument("-p", "--paranoidKey", help="Specify a custom key for zip files", dest="key2", action="store_true")
    parser.add_argument("-z", "--zipped", help="Zips the files and encrypts the zipped file using a different key.", action="store_true")
    parser.add_argument("-t", "--trash", help="Deletes the original file/directory", action="store_true")
    parser.add_argument("-d", "--decrypt", help="Decrypts all encrypted files in a directory or zip file", action="store_true")
    parser.add_argument("-g", "--get_keys", help="Copies the keys used to the same directory as the encrypted files", action="store_true")
else:
    parser.add_argument("-i", "--install", help="installs a the program", action="store_true")
args = parser.parse_args()

#install script
if not installed:
    if args.install:
        if not os.path.isdir(progdir): os.system("mkdir " + progdir)
        os.system("ssh-keygen -t rsa <<< \"" + progdir + "/rsa1\n\n\"")
        os.system("ssh-keygen -t rsa <<< \"" + progdir + "/rsa2\n\n\"")
        os.system("openssl rsa -in " + progdir + "/rsa1 -outform pem > " + progdir +"/rsa1.pem")
        os.system("openssl rsa -in " + progdir + "/rsa2 -outform pem > " + progdir +"/rsa2.pem")
        os.system("openssl rsa -in " + progdir + "/rsa1 -pubout -outform pem > " + progdir + "/rsa1.pub.pem")
        os.system("openssl rsa -in " + progdir + "/rsa2 -pubout -outform pem > " + progdir + "/rsa2.pub.pem")
        os.system("openssl rand -base64 32 > " + progdir + "/key1.bin")
        os.system("openssl rand -base64 32 > " + progdir + "/key2.bin")
        os.system("openssl rsautl -encrypt -inkey " + progdir + "/rsa1.pub.pem -pubin -in " + progdir + "/key1.bin -out " + progdir + "/key1.bin.enc")
        os.system("openssl rsautl -encrypt -inkey " + progdir + "/rsa2.pub.pem -pubin -in " + progdir + "/key2.bin -out " + progdir + "/key2.bin.enc")
        print("Take care of your keys in " + progdir + ", they're important!")
    sys.exit(0)

#check for valid pathname
if (not os.path.isfile(args.file_to_encrypt) and not os.path.isdir(args.file_to_encrypt)) or args.file_to_encrypt.endswith("/"):
    print("File not found")
    sys.exit(1)
if args.decrypt and not args.file_to_encrypt.endswith(".enc"):
    if not os.path.isdir(args.file_to_encrypt):
        print("Not a valid file to decrypt")
        sys.exit(1)
if not os.path.isfile(keyFile) or not os.path.isfile(paranoidKeyFile):
    print("Error, no two valid keyfiles given")
    sys.exit(1)

#determining mission parameters
isFile = False
isDir = False
isZip = False

if os.path.isdir(args.file_to_encrypt):
    isDir = True
elif args.file_to_encrypt.endswith(".zip.enc"):
    isZip = True
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
    os.system("zip -j " + file + ".zip " + file)
    if args.verbose: print("Deleting File " + file)
    os.system("rm " + file)

"""
Encrypts a zip file with a different key
@param zipfile - the zip file to be encrypted
"""
def encryptZipFile(zipFile):
    if args.verbose: print("encrypting zip file " + zipFile)
    os.system("openssl enc -aes-256-cbc -salt -in \"" + zipFile + "\" -out \"" + zipFile + ".enc\" -pass file:" + paranoidKeyFile)
    if args.verbose: print("created encrypted file " + zipFile + ".enc")
    if args.verbose: print("Deleting zip file " + zipFile)
    os.system("rm " + zipFile)

def decryptZipFile(encZipFile):
    if args.verbose: print("decrypting zip file " + encZipFile)
    newFile = encZipFile.split(".zip.enc")[0] + ".zip"
    os.system("openssl enc -d -aes-256-cbc -in \"" + encZipFile + "\" -out \"" + newFile + "\" -pass file:" + paranoidKeyFile)
    if args.verbose: print("created zipped file " + newFile)
    if args.trash:
        if args.verbose: print("Deleting encrypted zip file " + encZipFile)
        os.system("rm " + encZipFile)
    return newFile

def unzip(zippedFile):
    if args.verbose: print("unzipping " + zippedFile)
    newFile = zippedFile.split(".zip")[0]
    os.system("unzip " + zippedFile + " -d " + os.path.dirname(newFile))
    if args.verbose: print("deleting " + zippedFile)
    os.system("rm " + zippedFile)
    return newFile


#main routine

if not args.decrypt:
    if args.zipped:
        if args.trash:
            if isDir:
                encryptDirectory(args.file_to_encrypt, True, True)
                zipDirectory(args.file_to_encrypt + "_encrypted")
                encryptZipFile(args.file_to_encrypt + "_encrypted.zip")
            else:
                encryptFile(args.file_to_encrypt, True)
                zipFile(args.file_to_encrypt + ".enc")
                encryptZipFile(args.file_to_encrypt + ".enc.zip")
        else:
            if isDir:
                encryptDirectory(args.file_to_encrypt, False, True)
                zipDirectory(args.file_to_encrypt + "_encrypted")
                encryptZipFile(args.file_to_encrypt + "_encrypted.zip")
            else:
                encryptFile(args.file_to_encrypt, False)
                zipFile(args.file_to_encrypt + ".enc")
                encryptZipFile(args.file_to_encrypt + ".enc.zip")
    else:
        if args.trash:
            if isDir:
                encryptDirectory(args.file_to_encrypt, True, True)
                
            else:
                encryptFile(args.file_to_encrypt, True)
        else:
            if isDir:
                encryptDirectory(args.file_to_encrypt, False, True)
            else:
                encryptFile(args.file_to_encrypt, False)
else:
    if isZip:
        deCryptedZip = decryptZipFile(args.file_to_encrypt)
        unzipped = unzip(deCryptedZip)
        if os.path.isdir(unzipped): isDir = True
        else: isFile = True
        if args.trash:
            if isDir:
                decryptDirectory(unzipped, True)
            else:
                decryptfile(unzipped, True)
        else:
            if isDir:
                decryptDirectory(unzipped, False)
            else:
                decryptfile(unzipped, True)
    else:
        if args.trash:
            if isDir:
                decryptDirectory(args.file_to_encrypt, True)
            else:
                decryptfile(args.file_to_encrypt, True)
        else:
            if isDir:
                decryptDirectory(args.file_to_encrypt, False)
            else:
                decryptfile(args.file_to_encrypt, False)
