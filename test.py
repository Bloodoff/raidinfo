#!/usr/bin/python3
from lib.raid import RaidController
from lib.raid_3ware import RaidController3ware
from lib.raid_soft import RaidControllerSoft

controllers = RaidController.probe()
for controller in controllers:
    controller.printInfo()
