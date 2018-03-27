import os
import re

from . import helpers

from .raid import RaidController, RaidLD, RaidPD
from .mixins import TextAttributeParser
from .smart import SMARTinfo

if os.name == 'nt':
    raidUtil = 'C:\Program Files (x86)\Compaq\Hpacucli\Bin\hpacucli.exe'
else:
    raidUtil = '/opt/compaq/hpacucli/bld/hpacucli'


class RaidControllerHPSA(TextAttributeParser, RaidController):

    _attributes = [
        (r'^Smart\sArray\s(\S*)', 'Model', None, False, None),
        (r'^Serial\sNumber:\s(.*)$', 'Serial', None, False, None),
        (r'^Controller\sStatus:\s(.*)$', 'Status', None, False, None),
        (r'^Firmware\sVersion:\s(.*)$', 'Firmware', None, False, None),
        (r'^Cache\sBoard\sPresent:\s(.*)$', 'Cache', None, False, lambda match: match.group(1) == 'True'),
        (r'^Cache\sSerial\sNumber:\s(.*)$', 'CacheSerial', None, False, None),
        (r'^Cache\sStatus:\s(.*)$', 'CacheStatus', None, False, None),
        (r'^Cache\sStatus\sDetails:\s(.*)$', 'CacheStatusDetails', None, False, None),
        (r'^Total\sCache\sSize:\s(.*)$', 'CacheSize', None, False, None),
        (r'^Battery/Capacitor\sCount:\s(.*)$', 'CacheBatteryCount', None, False, None)
    ]

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
            print('Cache: {}, s/n {}, Battery count: {}, Status: {} / {}'.format(self.CacheSize,
                                                                                 self.CacheSerial,
                                                                                 self.CacheBatteryCount,
                                                                                 self.CacheStatus,
                                                                                 self.CacheStatusDetails))
        else:
            print('NO Cache module')

    def __fill_data(self):
        for line in helpers.getOutput('{} controller slot={} show'.format(raidUtil, self.Name)):
            if self._process_attributes_line(line):
                continue


class RaidLDvendorHPSA(TextAttributeParser, RaidLD):

    _attributes = [
        (r'^Disk\sName:\s(\S.*)$', 'Device', None, False, None),
        (r'^Size:\s(\S.*)$', 'Size', None, False, None),
        (r'^Fault\sTolerance:\s(\S.*)$', 'Level', None, False, None),
        (r'^Parity\sInitialization\sStatus:\s(.*)$', 'InitState', None, False, None),
        (r'^Parity\sInitialization\sProgress:\s(\S*)', 'InitProgress', '100%', False, None),
        (r'^Status:\s(\S.*)$', 'State', None, False, lambda match: {'OK': 'Optimal'}.get(match.group(1), match.group(1)))
    ]

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

    def printSpecificInfo(self):
        print('Rebuild state: {} ({})'.format(self.InitState, self.InitProgress))

    def __enumerate_pd(self):
        for line in helpers.getOutput('{} controller slot={} array {} physicaldrive all show'.format(raidUtil, self.Controller.Name, self.ArrayName)):
            match = re.search(r'^physicaldrive\s(\S+)', line)
            if match:
                self.PDs.append(RaidPDvendorHPSA(match.group(1), self))

    def __fill_data(self):
        self._set_default_attributes()
        for line in helpers.getOutput('{} controller slot={} logicaldrive {} show'.format(raidUtil, self.Controller.Name, self.Name)):
            if self._process_attributes_line(line):
                continue

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


class RaidPDvendorHPSA(TextAttributeParser, RaidPD):

    _attributes = [
        (r'^Status:\s(\S.*)$', 'State', None, False, lambda match: {'OK': 'Optimal'}.get(match.group(1), match.group(1))),
        (r'^Interface\sType:\s+(\S+)', 'Technology', None, False, None),
        (r'^Rotational\sSpeed:\s+(\d+)', 'RPM', None, False, None),
        (r'^PHY\sCount:\s+(\d+)', 'PHYCount', None, False, None),
        (r'(?i)^PHY\sTransfer\sRate:\s+(\S+)Gbps', 'PHYSpeed', None, False, None),
        (r'^Serial\sNumber:\s+(.+)$', 'Serial', None, False, None),
        (r'^Firmware\sRevision:\s+(.+)$', 'Firmware', None, False, None),
        (r'^Size:\s+(.+)$', 'Capacity', None, False, None),
        (r'^Model:\s+(.+)$', 'Model', None, False, None)
    ]

    def __init__(self, name, ld):
        super(self.__class__, self).__init__(name, ld)
        self.Device = name
        self.__fill_basic_info()
        self.__fill_advanced_info()

    def __fill_basic_info(self):
        for line in helpers.getOutput('{} controller slot={} physicaldrive {} show'.format(raidUtil, self.LD.Controller.Name, self.Device)):
            if self._process_attributes_line(line):
                continue
            match = re.search(r'^Drive\sType:\s+(\S.*$)', line)
            if match:
                if (match.group(1) == 'Spare Drive') and (self.State == 'Optimal'):
                    self.State = 'Hot spare'
                continue

    def __fill_advanced_info(self):
        smart = self.LD.search_smart_by_serial(self.Serial)
        if smart is not None:
            for prop in ['Model', 'Serial', 'Firmware', 'SectorSizes', 'FormFactor', 'PowerOnHours', 'ErrorCount', 'Temperature', 'Capacity', 'SCT']:
                if hasattr(smart, prop):
                    setattr(self, prop, getattr(smart, prop))
