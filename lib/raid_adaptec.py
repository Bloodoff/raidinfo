import os
import re
import xml.etree.ElementTree as ET

from . import helpers

from .raid import RaidController, RaidLD, RaidPD, DeviceCapacity
from .mixins import TextAttributeParser
from .smart import SMARTinfo

if os.name == 'nt':
    raidUtil = 'C:\\Program Files\\Adaptec\\maxView Storage Manager\\arcconf.exe'
else:
    raidUtil = '/usr/sbin/arcconf'


class RaidControllerAdaptec(TextAttributeParser, RaidController):

    _attributes = [
        (r'Controller\sModel\s+:\s(.*)$', 'Model', None, False, None),
        (r'Controller\sSerial\sNumber\s+:\s(.*)$', 'Serial', None, False, None),
        (r'Temperature\s+:\s(\d+)', 'Temperature', None, False, None),
        (r'(?i)Installed\smemory\s+:\s(.*)$', 'CacheSize', None, False, None),
        (r'Controller\sStatus\s+:\s(.*)$', 'Status', None, False, None),
        (r'BIOS\s+:\s(.*)$', 'BIOS', None, False, None),
        (r'Firmware\s+:\s(.*)$', 'Firmware', None, False, None)
    ]

    def __init__(self, name):
        super(self.__class__, self).__init__(name)
        self.Type = 'Adaptec'
        self.Serial = '-'
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
            if re.match(r'(?i)Logical\sdevice\sinformation', line):
                ld_section = True
                continue
            if not ld_section:
                continue
            if re.match(r'(?i)Physical\sdevice\sinformation', line):
                break
            match = re.search(r'(?i)Logical\sDevice\snumber\s(\d+)', line)
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
            if re.match(r'(?i)Logical\sdevice\sinformation', line):
                break
            if self._process_attributes_line(line):
                continue


class RaidLDvendorAdaptec(TextAttributeParser, RaidLD):

    _attributes = [
        (r'(?i)^Logical\sDevice\sname\s+:\s(.*)$', 'Device', '-', False, None),
        (r'(?i)^RAID\slevel\s+:\s(\d*)', 'Level', '-', False, lambda match: 'RAID{}'.format(match.group(1))),
        (r'(?i)^Status\sof\sLogical\sDevice\s+:\s(.*)$', 'State', '-', False, None),
        (r'(?i)^Size\s+:\s(.*)$', 'Size', '-', False, lambda match: '{}'.format(DeviceCapacity(match.group(1), 'MiB'))),
        (r'(?i)^Read-cache\ssetting\s+:\s(.*)$', 'CacheRSet', None, False, None),
        (r'(?i)^Read-cache\sstatus\s+:\s(.*)$', 'CacheRStatus', None, False, None),
        (r'(?i)^Write-cache\sstatus\s+:\s(.*)$', 'CacheWSet', None, False, None),
        (r'(?i)^Write-cache\ssetting\s+:\s(.*)$', 'CacheWStatus', None, False, None),
        (r'(?i)^maxCache\sread\scache\ssetting\s+:\s(.*)$', 'CacheMSet', None, False, None),
        (r'(?i)^maxCache\sread\scache\sstatus\s+:\s(.*)$', 'CacheMStatus', None, False, None)
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
        start_string = r'(?i)Logical Device number {}'.format(self.Name)
        ld_section = False
        for line in helpers.getOutput('{} GETCONFIG {}'.format(raidUtil, self.Controller.Name)):
            if re.match(start_string, line):
                ld_section = True
                continue
            if not ld_section:
                continue
            if re.match(r'(?i)Physical\sDevice\sinformation', line):
                break
            if re.match(r'(?i)Logical\sDevice\snumber\s(\d+)', line):
                break
            if self._process_attributes_line(line):
                continue
            match = re.search(r'(?i)^Segment\s(\d+)\s.*\s(\S+)$', line)
            if match:
                self.PDs.append(RaidPDvendorAdaptec('Seg: {}'.format(match.group(1)), self, match.group(2)))
                continue
            match = re.search(r'(?i)^Group\s(\d+),\sSegment\s(\d+)\s.*\s(\S+)$', line)
            if match:
                self.PDs.append(RaidPDvendorAdaptec('G:{!s:2} Seg:{}'.format(match.group(1), match.group(2)), self, match.group(3)))
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
            if re.match(r'(?i)Physical\sDevice\sinformation', line):
                pd_section = True
                continue
            if not pd_section:
                continue
            if re.match(r'(?i)Connector\sinformation', line):
                break
            if searched_pd and re.search(r'(?i)Device\s#\d+$', line):
                break
            match = re.search(r'(?i)Serial\snumber\s+:\s(.*)$', line)
            if match and (match.group(1) == self.Serial):
                searched_pd = True
                continue
            match = re.search(r'(?i)^State\s+:\s(.*)$', line)
            if match:
                self.State = match.group(1)
                continue
            match = re.search(r'(?i)^Transfer\sSpeed\s+:\s(\S*)\s(\S*)\s', line)
            if match:
                self.Technology = match.group(1)
                self.PHYSpeed = match.group(2)
                self.PHYCount = 0
                continue
            match = re.search(r'(?i)^Reported\sChannel.*:.*\((\S+)\)$', line)
            if match:
                self.Slot = match.group(1)
                continue
            if re.match(r'(?i)^Vendor\s+:$', line):
                self.Model = ''
                continue
            match = re.search(r'(?i)^Vendor\s+:\s(.*)$', line)
            if match:
                self.Model = match.group(1)
                continue
            match = re.search(r'(?i)^Model\s+:\s(.*)$', line)
            if match:
                self.Model = self.Model + ' ' + match.group(1)
                continue
            match = re.search(r'(?i)^Firmware\s+:\s(.*)$', line)
            if match:
                self.Firmware = match.group(1)
                continue
            match = re.search(r'(?i)^Total\sSize\s+:\s(.*)$', line)
            if match:
                self.Capacity = DeviceCapacity(match.group(1), 'MiB')
                continue
            match = re.search(r'^(?i)Phy\s#\d+$', line)
            if match:
                self.PHYCount = self.PHYCount + 1
                continue

    def __fill_smart_info(self):
        coordinates = self.Slot.split(':')
        smart = SMARTinfo('-d aacraid,{},{},{}'.format(int(self.LD.Controller.Name) - 1, coordinates[1], coordinates[0]), '/dev/null')
        if smart.SMART:
            if self.PHYCount == 0:
                delattr(self, 'PHYCount')
            for prop in ['SectorSizes', 'FormFactor', 'Temperature', 'RPM', 'PHYCount']:
                if not hasattr(self, prop):
                    if hasattr(smart, prop):
                        setattr(self, prop, getattr(smart, prop))

    def __fill_advanced_info(self):
        coordinates = self.Slot.split(':')
        smart = self.LD.Controller.find_SMART(coordinates[1], coordinates[0])
        if smart is None:
            return
        self.ErrorCount = 0
        for attribute in smart:
            value = int(attribute.attrib['rawValue']) if ('rawValue' in attribute.attrib) else int(attribute.attrib['Value'])
            if attribute.attrib['name'] == 'Power-On Hours':
                self.PowerOnHours = value
                continue
            if attribute.attrib['name'] in ['Current Internal Temperature', 'Current Drive Temperature in Celcius']:
                self.Temperature = value
                continue
            if attribute.attrib['name'] in ['Reallocated Sectors Count',
                                            'Reallocation Event Count',
                                            'Current Pending Sector Count',
                                            'Uncorrectable Sector Count',
                                            'Length of Defect List',
                                            'Total Uncorrected Read Errors',
                                            'Total Uncorrected Write Errors'
                                            ]:
                self.ErrorCount = value
                continue
