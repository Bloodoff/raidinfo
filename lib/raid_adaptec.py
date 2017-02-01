import os
import re
import xml.etree.ElementTree as ET

from . import helpers

from .raid import RaidController, RaidLD, RaidPD, DeviceCapacity
from .mixins import TextAttributeParser
from .smart import SMARTinfo

if os.name == 'nt':
    raidUtil = 'C:\Program Files\Adaptec\maxView Storage Manager\arcconf.exe'
else:
    raidUtil = '/usr/sbin/arcconf'


class RaidControllerAdaptec(TextAttributeParser, RaidController):

    _attributes = [
        (r'Controller\sModel\s+:\s(.*)$', 'Model', None, None),
        (r'Controller\sSerial\sNumber\s+:\s(.*)$', 'Serial', None, None),
        (r'Temperature\s+:\s(\d+)', 'Temperature', None, None),
        (r'Installed\smemory\s+:\s(.*)$', 'CacheSize', None, None),
        (r'Controller\sStatus\s+:\s(.*)$', 'Status', None, None),
        (r'BIOS\s+:\s(.*)$', 'BIOS', None, None),
        (r'Firmware\s+:\s(.*)$', 'Firmware', None, None)
    ]

    def __init__(self, name):
        super(self.__class__, self).__init__(name)
        self.Type = 'Adaptec'
        self.__fill_data()
        self.__load_SMART()
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

    def __load_SMART(self):
        self.SMART = []
        lines = helpers.getOutput('{} GETSMARTSTATS {}'.format(raidUtil, self.Name))
        lines = filter(lambda line: re.match(r'^<', line), lines)
        root = ET.fromstring('<data>' + ''.join(lines) + '</data>')
        for child in root:
            for child in child:
                self.SMART.append(child)

    def find_SMART(self, channel, id):
        for smart in self.SMART:
            if (smart.tag == 'PhysicalDriveSmartStats') and (smart.attrib['channel'] == channel) and (smart.attrib['id'] == id):
                return smart

    def printSpecificInfo(self):
        print('Model: {}, s/n {}'.format(self.Model, self.Serial))
        print('Cache: {}, status: {}'.format(self.CacheSize, self.Status))
        print('BIOS version: {}'.format(self.BIOS))
        print('FW version  : {}'.format(self.Firmware))
        print('CPU temperature: {}'.format(self.Temperature))

    def __fill_data(self):
        for line in helpers.getOutput('{} GETCONFIG {}'.format(raidUtil, self.Name)):
            if line == 'Logical device information':
                break
            if self._process_attributes_line(line):
                continue


class RaidLDvendorAdaptec(TextAttributeParser, RaidLD):

    _attributes = [
        (r'Logical\sDevice\sname\s+:\s(.*)$', 'Device', '-', None),
        (r'RAID\slevel\s+:\s(\d*)', 'Level', '-', lambda match: 'RAID{}'.format(match.group(1))),
        (r'Status\sof\sLogical\sDevice\s+:\s(.*)$', 'State', '-', None),
        (r'Size\s+:\s(.*)$', 'Size', '-', lambda match: '{}'.format(DeviceCapacity(match.group(1), 'MiB'))),
        (r'Read-cache\ssetting\s+:\s(.*)$', 'CacheRSet', None, None),
        (r'Read-cache\sstatus\s+:\s(.*)$', 'CacheRStatus', None, None),
        (r'Write-cache\sstatus\s+:\s(.*)$', 'CacheWSet', None, None),
        (r'Write-cache\ssetting\s+:\s(.*)$', 'CacheWStatus', None, None),
        (r'maxCache\sread\scache\ssetting\s+:\s(.*)$', 'CacheMSet', None, None),
        (r'maxCache\sread\scache\sstatus\s+:\s(.*)$', 'CacheMStatus', None, None)
    ]

    def __init__(self, name, controller):
        super(self.__class__, self).__init__(name, controller)
        self._set_default_attributes()
        self.__fill_data()
        self.DriveCount = len(self.PDs)
        self.DriveActiveCount = self.DriveCount

    def printSpecificInfo(self):
        if hasattr(self, 'CacheRSet'):
            print('Read cache : {} - {}'.format(self.CacheRSet, self.CacheRStatus))
        if hasattr(self, 'CacheWSet'):
            print('Write cache: {} - {}'.format(self.CacheWSet, self.CacheWStatus))
        if hasattr(self, 'CacheMSet'):
            print('maxCache   : {} - {}'.format(self.CacheMSet, self.CacheMStatus))

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
            if self._process_attributes_line(line):
                continue
            match = re.search(r'Segment\s(\d+)\s.*\s(\S+)$', line)
            if match:
                self.PDs.append(RaidPDvendorAdaptec(match.group(1), self, match.group(2)))
                continue


class RaidPDvendorAdaptec(RaidPD):

    def __init__(self, name, ld, serial):
        super(self.__class__, self).__init__(name, ld)
        self.Serial = serial
        self.Device = name
        self.PHYCount = 0
        self.__fill_basic_info()
        self.__fill_smart_info()
        self.__fill_advanced_info()

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
            if re.match(r'^Vendor\s+:$', line):
                self.Model = ''
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
                self.Capacity = DeviceCapacity(match.group(1), 'MiB')
                continue
            match = re.search(r'^Phy\s#\d+$', line)
            if match:
                self.PHYCount = self.PHYCount + 1
                continue

    def __fill_smart_info(self):
        coordinates = self.Slot.split(':')
        smart = SMARTinfo('-d aacraid,{},{},{}'.format(int(self.LD.Controller.Name) - 1, coordinates[1], coordinates[0]), '/dev/null')
        if smart.SMART:
            for prop in ['SectorSizes', 'FormFactor', 'Temperature', 'RPM']:
                if hasattr(smart, prop):
                    setattr(self, prop, getattr(smart, prop))

    def __fill_advanced_info(self):
        coordinates = self.Slot.split(':')
        smart = self.LD.Controller.find_SMART(coordinates[1], coordinates[0])
        if smart is None:
            return
        self.ErrorCount = 0
        for attribute in smart:
            if attribute.attrib['name'] == 'Power-On Hours':
                self.PowerOnHours = int(attribute.attrib['rawValue'])
                continue
            if attribute.attrib['name'] == 'Current Internal Temperature':
                self.Temperature = int(attribute.attrib['rawValue'])
                continue
            if attribute.attrib['name'] in ['Reallocated Sectors Count', 'Reallocation Event Count', 'Current Pending Sector Count', 'Uncorrectable Sector Count']:
                self.ErrorCount = self.ErrorCount + int(attribute.attrib['rawValue'])
                continue
