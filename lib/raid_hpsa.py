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
        self.__load_all_smart()
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

    def __enumerate_all_hpsa_scsi_host(self):
        output = helpers.readFile('/proc/scsi/scsi')
        hp_scsi_controllers = []
        current_host = -1
        current_vendor_hp = False
        for line in output:
            match = re.search(r'^Host:', line)
            if match:
                current_host = current_host + 1
                current_vendor_hp = False
            match = re.search(r'^Vendor:\sHP', line)
            if match:
                current_vendor_hp = True
            match = re.search(r'^Type:\s+RAID', line)
            if match and current_vendor_hp:
                hp_scsi_controllers.append('/dev/sg{}'.format(current_host))
        return hp_scsi_controllers

    def __load_all_smart(self):
        self.__smart = []

        for host in self.__enumerate_all_hpsa_scsi_host():
            i = 0
            while True:
                smart = SMARTinfo(' -d cciss,{}'.format(i), host)
                if not smart.SMART:
                    break
                self.__smart.append(smart)
                i = i + 1

    def __enumerate_ld(self):
        for line in helpers.getOutput('{} controller slot={} array all show'.format(raidUtil, self.Name)):
            match = re.search(r'^array\s(\S+)\s', line)
            if match:
                array_name = match.group(1)
                for line in helpers.getOutput('{} controller slot={} array {} logicaldrive all show'.format(raidUtil, self.Name, array_name)):
                    match = re.search(r'^logicaldrive\s(\d+)\s', line)
                    if match:
                        self.LDs.append(RaidLDvHPSA(match.group(1), self, array_name))

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


class RaidLDvHPSA(RaidLD):
    def __init__(self, name, controller, array_name):
        super(self.__class__, self).__init__(name, controller)
        self.Device = self.Name
        self.ArrayName = array_name
        self.Level = ''
        self.State = ''
        self.Size = ''
        self.__enumerate_pd()
        self.DriveCount = len(self.PDs)
        self.DriveActiveCount = self.DriveCount

    def __enumerate_pd(self):
        for line in helpers.getOutput('{} controller slot={} array {} physicaldrive all show'.format(raidUtil, self.Controller.Name, self.ArrayName)):
            match = re.search(r'^physicaldrive\s(\S+)', line)
            if match:
                self.PDs.append(RaidPDvHPSA(match.group(1), self))


class RaidPDvHPSA(RaidPD):

    def __init__(self, name, ld):
        super(self.__class__, self).__init__(name, ld)
        self.Device = name
        self.__fill_basic_info()

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

