#!/usr/bin/python
import socket
import datetime
import sys
import os
from io import StringIO
from lib import *

def main():

    controllers = raid.RaidController.probe()
    for controller in controllers:
        controller.printInfo()


if __name__ == '__main__':
    main()

