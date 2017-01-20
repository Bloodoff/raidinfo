import re

from . import helpers

smartctl = "/usr/sbin/smartctl"


class SMARTinfo(object):
    def __init__(self, cmd):
        self.__load_values(self)
        self.__cmd = cmd

    def __load_values(self):
        for line in helpers.getOutput('{} {}'.format(smartctl, self.__cmd)):
            match = re.search(r'Model\sFamily:\s+(.*)$', line)
            if match:
                self.Vendor = match.group(1)
            match = re.search(r'Device\sModel:\s+(.*)$', line)
            if match:
                self.Model = match.group(1)
            match = re.search(r'Serial\sNumber:\s+(.*)$', line)
            if match:
                self.Serial = match.group(1)
            match = re.search(r'Firmware\sVersion:\s+(.*)$', line)
            if match:
                self.Firmware = match.group(1)
            match = re.search(r'User\sCapacity:.*\[(.*)\]$', line)
            if match:
                self.Capacity = match.group(1)
            match = re.search(r'Sector\sSizes:\s+(\d+)\D+(\d+)', line)
            if match:
                self.Sectors = [match.group(1), match.group(2)]
            match = re.search(r'Rotation\sRate:\s+(\d+)', line)
            if match:
                self.RPM = match.group(1)
            match = re.search(r'Form\sFactor:\s+(\S+)', line)
            if match:
                self.FormFactor = match.group(1)


