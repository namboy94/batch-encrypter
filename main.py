#!/usr/bin/env python

import os
import sys
import argparse
from sys import platform as _platform

if not _platform == "linux":
    print("This program only works on Linux!")
    sys.exit(1)

# hardcoded variables
keyfile = os.getenv("HOME") + "/.ssh/key.bin"

# argument parser
parser = argparse.ArgumentParser()
parser.add_argument("file_to_encrypt", help="the file or directory to encrypt")
parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
parser.add_argument("-z", "--zipped", help="zips the files and encypts the zipped file", action="store_true")
parser.add_argument("-i", "--individual-enc", help="when zipping, encypts every file individually ",
                    action="store_true")
parser.add_argument("-d", "--decrypt", help="decrypts all encrypted files in a directory or zip fle",
                    action="store_true")
args = parser.parse_args()
if not os.path.isfile(args.file_to_encypt) or args.file_to_encrypt.endswith("/"):
    print("File not found")
    sys.exit(1)


# functions
def encryptFile(file):
    os.system("openssl enc -aes-256-cbc -salt -in \"" + file + "\" -out \"" + file + ".enc\" -pass file:" + keyfile)


def encryptDirectory(directory):
    directoryContent = os.listdir(directory)
    for child in directoryContent:
        encryptFile(directory + "/" + child)


def zipDirectory(directory):
    os.system("zip -r " + directory + ".zip " + os.path.dirname(directory))
