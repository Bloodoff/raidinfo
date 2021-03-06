import os
import re
import struct

from . import helpers

from .raid import RaidController, RaidLD, RaidPD, DeviceCapacity
from .mixins import TextAttributeParser
from .smart import SMARTinfo

if os.name == 'nt':
    raidUtil = 'C:\\Program Files (x86)\\MegaRAID Storage Manager\\StorCLI64.exe'
elif 'VMkernel' in os.uname():
    raidUtil = '/opt/lsi/storcli/storcli'
else:
    raidUtil = '/opt/MegaRAID/storcli/storcli64'


class RaidControllerLSI(TextAttributeParser, RaidController):

    _attributes = [
        (r'(?i)^Model\s=\s(.*)$', 'Model', None, False, None),
        (r'(?i)^Serial\sNumber\s=\s(.*)$', 'Serial', None, False, None),
        (r'(?i)^Controller\sStatus\s=\s(.*)$', 'Status', None, False, None),
        (r'(?i)^Bios\sVersion\s=\s(.*)$', 'BIOS', None, False, None),
        (r'(?i)^Firmware\sVersion\s=\s(.*)$', 'Firmware', None, False, None),
        (r'(?i)^On\sBoard\sMemory\sSize\s=\s(.*)$', 'CacheSize', None, False, None),
        (r'(?i)^BBU\s=\s(.*)$', 'Battery', None, False, lambda match: {'Absent': False}.get(match.group(1), True)),
        (r'(?i)^BBU\sStatus\s=\s(.*)$', 'BatteryStatus', None, False, lambda match: {'32': 'Degraded'}.get(match.group(1), match.group(1)))
    ]

    def __init__(self, name):
        super(self.__class__, self).__init__(name)
        self.Type = 'LSIMegaRAID'
        self.Serial = '-'
        self.__fill_data()
        self.__enumerate_ld()

    @staticmethod
    def probe():
        if not os.path.isfile(raidUtil):
            return []
        output = helpers.getOutput('{} show nolog'.format(raidUtil))
        controllers = []
        for line in output:
            match = re.search(r'^(\d+)\s\S+\s+\d+', line)
            if match:
                controllers.append(match.group(1))
        return controllers

    def __enumerate_ld(self):
        ld_section = False
        for line in helpers.getOutput('{} /c{} show all nolog'.format(raidUtil, self.Name)):
            if re.match(r'(?i)^VD\sLIST\s:', line):
                ld_section = True
                continue
            if not ld_section:
                continue
            if re.match(r'(?i)Physical\sDrives.*', line):
                break
            match = re.search(r'(?i)(\d+/\d+)\s+', line)
            if match:
                self.LDs.append(RaidLDvendorLSI(match.group(1), self))

    def printSpecificInfo(self):
        print('Model: {}, s/n {}, {}'.format(self.Model, self.Serial, self.Status))
        print('Cache: {}'.format(self.CacheSize))
        if self.Battery:
            print('BBU status: {}'.format(self.BatteryStatus))
        print('BIOS version: {}'.format(self.BIOS))
        print('FW version  : {}'.format(self.Firmware))

    def __fill_data(self):
        for line in helpers.getOutput('{} /c{} show all nolog'.format(raidUtil, self.Name)):
            if re.match(r'(?i)^TOPOLOGY\s:', line):
                break
            if self._process_attributes_line(line):
                continue


class RaidLDvendorLSI(RaidLD):

    def __init__(self, name, controller):
        (self.DG, self.VD) = name.split('/')
        super(self.__class__, self).__init__(name, controller)
        self.Device = self.Name
        self.Level = ''
        self.State = ''
        self.Size = ''
        self.__fill_data()
        self.__find_devicename()
        self.__enumerate_pd()
        self.DriveCount = len(self.PDs)
        self.DriveActiveCount = self.DriveCount

    def __enumerate_pd(self):
        pd_section = False
        for line in helpers.getOutput('{} /c{}/v{} show all nolog'.format(raidUtil, self.Controller.Name, self.VD)):
            if re.match(r'(?i)PDs\sfor\sVD', line):
                pd_section = True
                continue
            if not pd_section:
                continue
            match = re.search(r'(?i)^(\d+):(\d+)\s+(\d+)\s+\S+', line)
            if match:
                self.PDs.append(RaidPDvendorLSI(match.group(1), match.group(2), match.group(3), self))

    def __fill_data(self):
        for line in helpers.getOutput('{} /c{}/v{} show all nolog'.format(raidUtil, self.Controller.Name, self.VD)):
            match = re.search(r'(?i)SCSI\sNAA\sId\s=\s(.*)$', line)
            if match:
                self.NAA = match.group(1)
            match = re.search(r'(?i)^(\d+)\/(\d+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)', line)
            if match:
                self.Level = match.group(3)
                self.State = {'Optl': 'Optimal',
                              'Rec': 'Recovery',
                              'OfLn': 'OffLine',
                              'Pdgd': 'Partially Degraded',
                              'Dgrd': 'Degraded'}.get(match.group(4), match.group(4))
                self.Size = DeviceCapacity(int(float(match.group(10)) * 1024), {'TB': 'GiB', 'GB': 'MiB', 'MB': 'KiB'}.get(match.group(11), None))

    def __find_devicename(self):
        try:
            for filename in [f for f in os.listdir('/dev/disk/by-id')]:
                match = re.search(r'^scsi-\d+' + self.NAA, filename)
                if match:
                    self.Device = '/dev/disk/by-id/' + filename
        except:
            pass


class RaidPDvendorLSI(TextAttributeParser, RaidPD):

    _attributes = [
        (r'(?i)^SN\s+=\s+(.*)$', 'Serial', None, False, None),
        (r'(?i)^Manufacturer\sId\s=\s+(.*)$', 'Vendor', None, False, None),
        (r'(?i)^Drive\sTemperature\s=\s+(\d+)C', 'Temperature', None, False, None),
        (r'(?i)^Model\sNumber\s=\s+(.*)$', 'Model', None, False, None),
        (r'(?i)^Media\sError\sCount\s=\s+(\d+)', 'ErrorCount', None, True, lambda match: int(match.group(1))),
        (r'(?i)^Predictive\sFailure\sCount\s=\s+(\d+)', 'ErrorCount', None, True, lambda match: int(match.group(1)))
    ]

    def __init__(self, enclosure, slot, did, ld):
        super(self.__class__, self).__init__('{}:{}'.format(enclosure, slot), ld)
        self.Enclosure = enclosure
        self.Slot = slot
        self.Device = did
        self.PHYCount = 0
        self.__fill_basic_info()
        if hasattr(self, 'Vendor'):
            self.Model = self.Vendor + ' ' + self.Model
        if 'VMkernel' in os.uname():
            self.__fill_LSI_smart_info()
        else:
            self.__fill_smart_info()

    def __fill_basic_info(self):
        for line in helpers.getOutput('{} /c{}/e{}/s{} show all nolog'.format(raidUtil, self.LD.Controller.Name, self.Enclosure, self.Slot)):
            match = re.search(r'^(\d+):(\d+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)', line)
            if match:
                self.Capacity = DeviceCapacity(int(float(match.group(6)) * 1024), {'TB': 'GiB', 'GB': 'MiB', 'MB': 'KiB'}.get(match.group(7), None))
                self.Technology = match.group(8)
                self.State = {
                    'DHS': 'Dedicated Hot Spare',
                    'UGood': 'Unconfigured Good',
                    'GHS': 'Global Hotspare',
                    'UBad': 'Unconfigured Bad',
                    'Onln': 'Optimal',
                    'Rbld': 'Rebuild',
                    'Offln': 'Offline'
                }.get(match.group(4), match.group(4))
            if self._process_attributes_line(line):
                continue

    def __fill_smart_info(self):
        smart = SMARTinfo('-d megaraid,{}'.format(int(self.Device)), self.LD.Device)
        if not smart.SMART:
            return
        for prop in ['Model', 'Serial', 'Firmware', 'Capacity', 'SectorSizes', 'FormFactor', 'PHYCount', 'PHYSpeed', 'RPM', 'PowerOnHours', 'ErrorCount', 'Temperature', 'SCT']:
            if hasattr(smart, prop):
                setattr(self, prop, getattr(smart, prop))

    def __fill_LSI_smart_info(self):
        data_dump = []
        for line in helpers.getOutput('{} /c{}/e{}/s{} show smart nolog'.format(raidUtil, self.LD.Controller.Name, self.Enclosure, self.Slot)):
            match = re.search(r'^(\S\S\s){15}\S\S$', line)
            if match:
                for c in line.split(' '):
                    data_dump.append(int(c, 16))
        data_dump = data_dump[2:]
        smart = {}
        for attr_index in range(0, len(data_dump) // 12):
            attr, value = struct.unpack('<BxxxxHxxxxx', bytearray(data_dump[attr_index * 12:(attr_index + 1) * 12]))
            if attr != 0:
                smart[attr] = value
        setattr(self, 'PowerOnHours', smart.get(9, None))
        setattr(self, 'ErrorCount', smart.get(5, 0) + smart.get(187, 0) + smart.get(196, 0) + smart.get(197, 0) + smart.get(198, 0))
