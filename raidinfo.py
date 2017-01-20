#!/usr/bin/python3
import os
import sys

from lib import *


def printUsage():
    print('Makes a compact report about RAID controllers')
    print('Usage: softraid.py')

if __name__ == '__main__':
    if os.getenv('USER') != 'root':
        print('This script requires Administrator privileges')
        sys.exit(5)

if len(sys.argv) > 1:
    printUsage()
    sys.exit(1)

controllers = raid.RaidController.probe()
for controller in controllers:
    controller.printInfo()
