#!/usr/bin/python
import os
import sys

from lib.raid import raidController
from lib.raid_soft import raidControllerSoft
from lib.raid_3ware import raidController3ware

controllers = raidController.probe()
for controller in controllers:
    controller.printInfo()
