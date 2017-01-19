#!/usr/bin/python
import os
import sys

from lib.raid import raidController
from lib.raid_soft import raidControllerSoft
from lib.raid_3ware import raidController3ware


def printUsage():
    print 'Makes a compact report about RAID controllers'
    print 'Usage: softraid.py'

if __name__ == '__main__':
    if os.getenv('USER') != 'root':
        print 'This script requires Administrator privileges'
        sys.exit(5)

if len(sys.argv) > 1:
    printUsage()
    sys.exit(1)

controllers = raidController.probe()
for controller in controllers:
    controller.printInfo()
