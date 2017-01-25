import os
import re

from . import helpers

from .raid import RaidController, RaidLD, RaidPD
from .smart import SMARTinfo

raidUtil = '/usr/sbin/arcconf'


class RaidControllerAdaptec(RaidController):

    def __init__(self, name):
        super(self.__class__, self).__init__(name)
        self.Type = 'Adaptec'
        self.__fill_data()
        self.__enumerate_ld()

    @staticmethod
    def probe():
        if not os.path.isfile(raidUtil):
            return []
        output = helpers.getOutput('{} LIST'.format(raidUtil))
        controllers = []
        for line in output:
            match = re.search(r'^Controller\s(\d+)\D', line)
            if match:
                controllers.append(match.group(1))
        return controllers

    def __enumerate_ld(self):
        ld_section = False
        for line in helpers.getOutput('{} GETCONFIG {}'.format(raidUtil, self.Name)):
            if line == 'Logical device information':
                ld_section = True
                continue
            if not ld_section:
                continue
            if line == 'Physical Device information':
                break
            match = re.search(r'Logical\sDevice\snumber\s(\d+)', line)
            if match:
                self.LDs.append(RaidLDvendorAdaptec(match.group(1), self))

    def printSpecificInfo(self):
        print('Model: {}, s/n {}, cache: {}, status: {}'.format(self.Model, self.Serial, self.CacheSize, self.Status))
        print('BIOS version: {}, FW version: {}'.format(self.BIOS, self.Firmware))
        print('CPU temperature: {}'.format(self.Temperature))

    def __fill_data(self):
        for line in helpers.getOutput('{} GETCONFIG {}'.format(raidUtil, self.Name)):
            if line == 'Logical device information':
                break
            match = re.search(r'Controller\sModel\s+:\s(.*)$', line)
            if match:
                self.Model = match.group(1)
                continue
            match = re.search(r'Controller\sSerial\sNumber\s+:\s(.*)$', line)
            if match:
                self.Serial = match.group(1)
                continue
            match = re.search(r'Temperature\s+:\s(\d+)', line)
            if match:
                self.Temperature = int(match.group(1))
                continue
            match = re.search(r'Installed\smemory\s+:\s(.*)$', line)
            if match:
                self.CacheSize = match.group(1)
                continue
            match = re.search(r'Controller\sStatus\s+:\s(.*)$', line)
            if match:
                self.Status = match.group(1)
                continue
            match = re.search(r'BIOS\s+:\s(.*)$', line)
            if match:
                self.BIOS = match.group(1)
                continue
            match = re.search(r'Firmware\s+:\s(.*)$', line)
            if match:
                self.Firmware = match.group(1)
                continue

class RaidLDvendorAdaptec(RaidLD):
    def __init__(self, name, controller):
        super(self.__class__, self).__init__(name, controller)
        self.Level = ''
        self.State = ''
        self.Size = ''
        self.__fill_data()
        #self.__load_all_smart()
        #self.__enumerate_pd()
        self.DriveCount = len(self.PDs)
        self.DriveActiveCount = self.DriveCount

    def printSpecificInfo(self):
        print('Read cache: {} - {}'.format(self.CacheRSet, self.CacheRStatus))
        print('Write cache: {} - {}'.format(self.CacheWSet, self.CacheWStatus))
        print('maxCache: {} - {}'.format(self.CacheMSet, self.CacheMStatus))

    def __fill_data(self):
        start_string = 'Logical Device number {}'.format(self.Name)
        ld_section = False
        for line in helpers.getOutput('{} GETCONFIG {}'.format(raidUtil, self.Controller.Name)):
            if line == start_string:
                ld_section = True
                continue
            if not ld_section:
                continue
            if line == 'Physical Device information':
                break
            if re.search(r'Logical\sDevice\snumber\s(\d+)', line):
                break
            match = re.search(r'Logical\sDevice\sname\s+:\s(.*)$', line)
            if match:
                self.Device = match.group(1)
                continue
            match = re.search(r'RAID\slevel\s+:\s(\d*)\s', line)
            if match:
                self.Level = 'RAID{}'.format(match.group(1))
                continue
            match = re.search(r'Status\sof\sLogical\sDevice\s+:\s(.*)$', line)
            if match:
                self.State = match.group(1)
                continue
            match = re.search(r'Size\s+:\s(.*)$', line)
            if match:
                self.Size = match.group(1)
                continue
            match = re.search(r'Read-cache\ssetting\s+:\s(.*)$', line)
            if match:
                self.CacheRSet = match.group(1)
                continue
            match = re.search(r'Read-cache\sstatus\s+:\s(.*)$', line)
            if match:
                self.CacheRStatus = match.group(1)
                continue
            match = re.search(r'Write-cache\ssetting\s+:\s(.*)$', line)
            if match:
                self.CacheWSet = match.group(1)
                continue
            match = re.search(r'Write-cache\sstatus\s+:\s(.*)$', line)
            if match:
                self.CacheWStatus = match.group(1)
                continue
            match = re.search(r'maxCache\sread\scache\ssetting\s+:\s(.*)$', line)
            if match:
                self.CacheMSet = match.group(1)
                continue
            match = re.search(r'maxCache\sread\scache\sstatus\s+:\s(.*)$', line)
            if match:
                self.CacheMStatus = match.group(1)
                continue
            match = re.search(r'Segment\s(\d+)\s.*\s(\S+)$', line)
            if match:
                self.PDs.append(RaidPDvendorAdaptec(match.group(1), self, match.group(2)))

class RaidPDvendorAdaptec(RaidPD):

    def __init__(self, name, ld, serial):
        super(self.__class__, self).__init__(name, ld)
        self.Serial = serial
        self.Device = name
        self.PHYCount = 0
        self.__fill_basic_info()
        #self.__fill_advanced_info()
        #
    
    def __fill_basic_info(self):
        pd_section = False
        searched_pd = False
        for line in helpers.getOutput('{} GETCONFIG {}'.format(raidUtil, self.LD.Controller.Name)):
            if line == 'Physical Device information':
                pd_section = True
                continue
            if not pd_section:
                continue
            if line == 'Connector information':
                break
            if searched_pd and re.search(r'Device\s#\d+$', line):
                break
            match = re.search(r'Serial\snumber\s+:\s(.*)$', line)
            if match and (match.group(1) == self.Serial):
                searched_pd = True
                continue
            match = re.search(r'^State\s+:\s(.*)$', line)
            if match:
                self.State = match.group(1)
                continue
            match = re.search(r'^Transfer\sSpeed\s+:\s(\S*)\s(\S*)\s', line)
            if match:
                self.Technology = match.group(1)
                self.PHYSpeed = match.group(2)
                self.PHYCount = 0
                continue
            match = re.search(r'^Reported\sChannel.*:.*\((\S+)\)$', line)
            if match:
                self.Slot = match.group(1)
                continue
            match = re.search(r'^Vendor\s+:\s(.*)$', line)
            if match:
                self.Model = match.group(1)
                continue
            match = re.search(r'^Model\s+:\s(.*)$', line)
            if match:
                self.Model = self.Model + ' ' + match.group(1)
                continue
            match = re.search(r'^Firmware\s+:\s(.*)$', line)
            if match:
                self.Firmware = match.group(1)
                continue
            match = re.search(r'^Total\sSize\s+:\s(.*)$', line)
            if match:
                self.Capacity = match.group(1)
                continue
            match = re.search(r'^Phy\s#\d+$', line)
            if match:
                self.PHYCount = self.PHYCount + 1
                continue
            