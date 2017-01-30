import os
import re

from . import helpers

from .raid import RaidController, RaidLD, RaidPD

raidUtil = '/usr/sbin/tw_cli'


class RaidController3ware(RaidController):

    def __init__(self, name):
        super(self.__class__, self).__init__(name)
        self.Type = '3ware'
        self.Model = self.__getModel()
        self.Cache = self.__getCache()
        self.__enumerateLD()

    @staticmethod
    def probe():
        if not os.path.isfile(raidUtil):
            return []
        output = helpers.getOutput('{} show'.format(raidUtil))
        controllers = []
        for line in output:
            match = re.search(r'^c(\d+)\s', line)
            if match:
                controllers.append(match.group(1))
        return controllers

    def __enumerateLD(self):
        for line in helpers.getOutput('{} /c{} show'.format(raidUtil, self.Name)):
            match = re.search(r'^u(\d+)\s', line)
            if match:
                self.LDs.append(RaidLD3ware(match.group(1), self))

    def printSpecificInfo(self):
        print('Model: {}, cache memory: {}'.format(self.Model, self.Cache))

    def __getModel(self):
        for line in helpers.getOutput('{} /c{} show all'.format(raidUtil, self.Name)):
            match = re.search(r'^\/c\d+\sModel\s=\s(.*)$', line)
            if match:
                return match.group(1)
        return '-'

    def __getCache(self):
        for line in helpers.getOutput('{} /c{} show all'.format(raidUtil, self.Name)):
            match = re.search(r'^\/c\d+\sAvailable\sMemory\s=\s(.*)$', line)
            if match:
                return match.group(1)
        return '-'


class RaidLD3ware(RaidLD):
    def __init__(self, name, controller):
        super(self.__class__, self).__init__(name, controller)
        self.Device = self.Name
        self.Level = self.__getLDlevel()
        self.State = self.__getLDstate()
        self.Size = self.__getLDsize()
        self.__enumeratePD()
        self.DriveActiveCount = self.DriveCount

    def __enumeratePD(self):
        for line in helpers.getOutput('{} /c{}/u{} show all'.format(raidUtil, self.Controller.Name, self.Name)):
            match = re.search(r'^u.*DISK.*\sp(\d+)\s', line)
            if match:
                self.PDs.append(RaidPD3ware(match.group(1), self))

        self.DriveCount = len(self.PDs)

    def __getLDlevel(self):
        for line in helpers.getOutput('{} /c{}/u{} show all'.format(raidUtil, self.Controller.Name, self.Name)):
            match = re.search(r'^u\d+\s+(\S+)', line)
            if match:
                return match.group(1)
        return '-'

    def __getLDstate(self):
        for line in helpers.getOutput('{} /c{}/u{} show all'.format(raidUtil, self.Controller.Name, self.Name)):
            match = re.search(r'\/c\d+\/u\d+\sstatus\s=\s(.*)$', line)
            if match:
                return {'OK': 'Optimal'}.get(match.group(1), match.group(1))
        return '-'

    def __getLDsize(self):
        for line in helpers.getOutput('{} /c{}/u{} show all'.format(raidUtil, self.Controller.Name, self.Name)):
            match = re.search(r'^u\d+\s+.*\s(\d+)', line)
            if match:
                return '{} GiB'.format(match.group(1))
        return '0 GiB'


class RaidPD3ware(RaidPD):

    def __init__(self, name, ld):
        super(self.__class__, self).__init__(name, ld)
        self.Device = name
        self.Technology = self.__getTechnology()
        self.Slot = name
        self.State = self.__getState()
        self.Model = self.__getModel()
        self.Serial = self.__getSerial()
        self.Firmware = self.__getFirmware()
        self.Capacity = self.__getCapacity()
        self.RPM = self.__getRPM()
        self.Speed = self.__getSpeed()
        self.PowerOnHours = self.__getPowerOnHours()
        self.BadSectorsCount = self.__getBadSectorsCount()
        self.Tempreature = self.__getTemperature()

    def __getState(self):
        for line in helpers.getOutput('{} /c{}/p{} show all'.format(raidUtil, self.LD.Controller.Name, self.Name)):
            match = re.search(r'\/c\d+\/p\d+\sStatus\s=\s(.*)$', line)
            if match:
                return {'OK': 'Optimal'}.get(match.group(1), match.group(1))
        return '-'

    def __getModel(self):
        for line in helpers.getOutput('{} /c{}/p{} show all'.format(raidUtil, self.LD.Controller.Name, self.Name)):
            match = re.search(r'\/c\d+\/p\d+\sModel\s=\s(.*)$', line)
            if match:
                return match.group(1)
        return '-'

    def __getSerial(self):
        for line in helpers.getOutput('{} /c{}/p{} show all'.format(raidUtil, self.LD.Controller.Name, self.Name)):
            match = re.search(r'\/c\d+\/p\d+\sSerial\s=\s(.*)$', line)
            if match:
                return match.group(1)
        return '-'

    def __getFirmware(self):
        for line in helpers.getOutput('{} /c{}/p{} show all'.format(raidUtil, self.LD.Controller.Name, self.Name)):
            match = re.search(r'\/c\d+\/p\d+\sFirmware\sVersion\s=\s(.*)$', line)
            if match:
                return match.group(1)
        return '-'

    def __getCapacity(self):
        for line in helpers.getOutput('{} /c{}/p{} show all'.format(raidUtil, self.LD.Controller.Name, self.Name)):
            match = re.search(r'\/c\d+\/p\d+\sCapacity\s=\s(.*)\s\(', line)
            if match:
                return match.group(1)
        return 0

    def __getRPM(self):
        for line in helpers.getOutput('{} /c{}/p{} show all'.format(raidUtil, self.LD.Controller.Name, self.Name)):
            match = re.search(r'\/c\d+\/p\d+\sSpindle\sSpeed\s=\s(\d*)\s', line)
            if match:
                return match.group(1)
        return '-'

    def __getSpeed(self):
        for line in helpers.getOutput('{} /c{}/p{} show all'.format(raidUtil, self.LD.Controller.Name, self.Name)):
            match = re.search(r'\/c\d+\/p\d+\sLink\sSpeed\s=\s(.*)\s', line)
            if match:
                return match.group(1)
        return '-'

    def __getPowerOnHours(self):
        for line in helpers.getOutput('{} /c{}/p{} show all'.format(raidUtil, self.LD.Controller.Name, self.Name)):
            match = re.search(r'\/c\d+\/p\d+\sPower\sOn\sHours\s=\s(\d*)$', line)
            if match:
                return match.group(1)
        return 0

    def __getBadSectorsCount(self):
        for line in helpers.getOutput('{} /c{}/p{} show all'.format(raidUtil, self.LD.Controller.Name, self.Name)):
            match = re.search(r'\/c\d+\/p\d+\sReallocated\sSectors\s=\s(\d*)$', line)
            if match:
                return match.group(1)
        return 0

    def __getTemperature(self):
        for line in helpers.getOutput('{} /c{}/p{} show all'.format(raidUtil, self.LD.Controller.Name, self.Name)):
            match = re.search(r'\/c\d+\/p\d+\sTemperature\s=\s(\d*)\s', line)
            if match:
                return match.group(1)
        return '-'

    def __getTechnology(self):
        for line in helpers.getOutput('{} /c{}/p{} show all'.format(raidUtil, self.LD.Controller.Name, self.Name)):
            match = re.search(r'\/c\d+\/p\d+\sDrive\sType\s=\s(.*)$', line)
            if match:
                return match.group(1)
        return '-'
