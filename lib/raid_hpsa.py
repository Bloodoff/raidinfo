import os
import re

from . import helpers

from .raid import RaidController, RaidLD, RaidPD
from .smart import SMARTinfo

raidUtil = '/opt/compaq/hpacucli/bld/hpacucli'


class RaidControllerHPSA(RaidController):

    def __init__(self, name):
        super(self.__class__, self).__init__(name)
        self.Type = 'HPSA'
        self.CacheStatusDetails = ''
        self.__fill_data()
        self.__enumerate_ld()

    @staticmethod
    def probe():
        if not os.path.isfile(raidUtil):
            return []
        output = helpers.getOutput('{} controller all show'.format(raidUtil))
        controllers = []
        for line in output:
            match = re.search(r'^Smart\s.*Slot\s(\d+)\s', line)
            if match:
                controllers.append(match.group(1))
        return controllers

    def __enumerate_ld(self):
        for line in helpers.getOutput('{} controller slot={} array all show'.format(raidUtil, self.Name)):
            match = re.search(r'^array\s(\S+)\s', line)
            if match:
                array_name = match.group(1)
                for line in helpers.getOutput('{} controller slot={} array {} logicaldrive all show'.format(raidUtil, self.Name, array_name)):
                    match = re.search(r'^logicaldrive\s(\d+)\s', line)
                    if match:
                        self.LDs.append(RaidLDvendorHPSA(match.group(1), self, array_name))

    def printSpecificInfo(self):
        print('Model: {}, s/n: {}, fw: {}, Status: {}'.format(self.Model, self.Serial, self.Firmware, self.Status))
        if self.Cache:
            print('Cache: {}, s/n {}, Battery count: {}, Status: {} / {}'.format(self.CacheSize, self.CacheSerial, self.CacheBatteryCount, self.CacheStatus, self.CacheStatusDetails))
        else:
            print('NO Cache module')

    def __fill_data(self):
        for line in helpers.getOutput('{} controller slot={} show'.format(raidUtil, self.Name)):
            match = re.search(r'^Smart\sArray\s(\S*)', line)
            if match:
                self.Model = match.group(1)
            match = re.search(r'^Serial\sNumber:\s(.*)$', line)
            if match:
                self.Serial = match.group(1)
            match = re.search(r'^Controller\sStatus:\s(.*)$', line)
            if match:
                self.Status = match.group(1)
            match = re.search(r'^Firmware\sVersion:\s(.*)$', line)
            if match:
                self.Firmware = match.group(1)
            match = re.search(r'^Cache\sBoard\sPresent:\s(.*)$', line)
            if match:
                if match.group(1) == 'True':
                    self.Cache = True
                else:
                    self.Cache = False
            match = re.search(r'^Cache\sSerial\sNumber:\s(.*)$', line)
            if match:
                self.CacheSerial = match.group(1)
            match = re.search(r'^Cache\sStatus:\s(.*)$', line)
            if match:
                self.CacheStatus = match.group(1)
            match = re.search(r'^Cache\sStatus\sDetails:\s(.*)$', line)
            if match:
                self.CacheStatusDetails = match.group(1)
            match = re.search(r'^Total\sCache\sSize:\s(.*)$', line)
            if match:
                self.CacheSize = match.group(1)
            match = re.search(r'^Battery/Capacitor\sCount:\s(.*)$', line)
            if match:
                self.CacheBatteryCount = match.group(1)


class RaidLDvendorHPSA(RaidLD):
    def __init__(self, name, controller, array_name):
        super(self.__class__, self).__init__(name, controller)
        self.ArrayName = array_name
        self.Level = ''
        self.State = ''
        self.Size = ''
        self.__fill_data()
        self.__load_all_smart()
        self.__enumerate_pd()
        self.DriveCount = len(self.PDs)
        self.DriveActiveCount = self.DriveCount

    def __enumerate_pd(self):
        for line in helpers.getOutput('{} controller slot={} array {} physicaldrive all show'.format(raidUtil, self.Controller.Name, self.ArrayName)):
            match = re.search(r'^physicaldrive\s(\S+)', line)
            if match:
                self.PDs.append(RaidPDvendorHPSA(match.group(1), self))

    def __fill_data(self):
        for line in helpers.getOutput('{} controller slot={} logicaldrive {} show'.format(raidUtil, self.Controller.Name, self.Name)):
            match = re.search(r'^Disk\sName:\s(\S.*)$', line)
            if match:
                self.Device = match.group(1)
            match = re.search(r'^Size:\s(\S.*)$', line)
            if match:
                self.Size = match.group(1)
            match = re.search(r'^Fault\sTolerance:\s(\S.*)$', line)
            if match:
                self.Level = match.group(1)
            match = re.search(r'^Status:\s(\S.*)$', line)
            if match:
                self.State = {'OK': 'Optimal'}.get(match.group(1), match.group(1))

    def __load_all_smart(self):
        self.__smart = []
        i = 0
        while True:
            smart = SMARTinfo(' -d cciss,{}'.format(i), self.Device)
            if not smart.SMART:
                break
            self.__smart.append(smart)
            i = i + 1

    def search_smart_by_serial(self, serial):
        for smart in self.__smart:
            if (smart.Serial in serial) or (serial in smart.Serial):
                return smart
        return None


class RaidPDvendorHPSA(RaidPD):

    def __init__(self, name, ld):
        super(self.__class__, self).__init__(name, ld)
        self.Device = name
        self.__fill_basic_info()
        self.__fill_advanced_info()

    def __fill_basic_info(self):
        for line in helpers.getOutput('{} controller slot={} physicaldrive {} show'.format(raidUtil, self.LD.Controller.Name, self.Device)):
            match = re.search(r'^Status:\s+(\S.*)$', line)
            if match:
                self.State = {'OK': 'Optimal'}.get(match.group(1), match.group(1))
            match = re.search(r'^Drive\sType:\s+(\S.*$)', line)
            if match:
                if (match.group(1) == 'Spare Drive') and (self.State == 'Optimal'):
                    self.State = 'Hot spare'
            match = re.search(r'^Interface\sType:\s+(\S+)', line)
            if match:
                self.Technology = match.group(1)
            match = re.search(r'^Rotational\sSpeed:\s+(\d+)', line)
            if match:
                self.RPM = match.group(1)
            match = re.search(r'^PHY\sCount:\s+(\d+)', line)
            if match:
                self.PHYCount = int(match.group(1))
            match = re.search(r'^PHY\sTransfer\sRate:\s+(\S+)Gbps', line)
            if match:
                self.PHYSpeed = match.group(1)
            match = re.search(r'^Serial\sNumber:\s+(\S+)', line)
            if match:
                self.Serial = match.group(1)

    def __fill_advanced_info(self):
        smart = self.LD.search_smart_by_serial(self.Serial)
        if smart is not None:
            for prop in ['Model', 'Serial', 'Firmware', 'SectorSizes', 'FormFactor', 'PowerOnHours', 'ErrorCount', 'Temperature', 'Capacity']:
                if hasattr(smart, prop):
                    setattr(self, prop, getattr(smart, prop))
