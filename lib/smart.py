import re
import os

from . import helpers
from .mixins import TextAttributeParser

if os.name == 'nt':
    smartctl = 'C:\\Program Files\\smartmontools\\bin\\smartctl.exe'
else:
    smartctl = '/usr/sbin/smartctl'


class SMARTinfo(TextAttributeParser):
    _attributes = [
        (r'Model\sFamily:\s+(.*)$'                     , 'Vendor'      , None, False, None),
        (r'Device\sModel:\s+(.*)$'                     , 'Model'       , None, False, None),
        (r'Serial\s[N|n]umber:\s+(.*)$'                , 'Serial'      , None, False, None),
        (r'Firmware\sVersion:\s+(.*)$'                 , 'Firmware'    , None, False, None),
        (r'User\sCapacity:.*\[(.*)\]$'                 , 'Capacity'    , None, False, None),
        (r'Rotation\sRate:\s+(\d+)'                    , 'RPM'         , None, False, None),
        (r'Form\sFactor:\s+(\S+)'                      , 'FormFactor'  , None, False, None),
        (r'SATA Version is:.+\s(\S+)\sGb\/s'           , 'PHYSpeed'    , None, False, None),
        (r'number\sof\sphys\s=\s(\d+)'                 , 'PHYCount'    ,    0,  True, lambda match: int(match.group(1))),
        (r'194\sTemperature_Celsius.*\s(\d+)(?:\s\(|$)', 'Temperature' , None, False, None),
        (r'9\sPower_On_Hours+.*\s(\d+)$'               , 'PowerOnHours', None, False, None),
        (r'Vendor:\s+(\S.*)$'                          , 'Vendor'      , None, False, None),
        (r'Revision:\s+(\S.*)$'                        , 'Firmware'    , None, False, None),
        (r'Current\sDrive\sTemperature:\s+(\d*)'       , 'Temperature' , None, False, None),
        (r'number\sof\shours\spowered\sup\s=\s+(\d*)'  , 'PowerOnHours', None, False, None),
        (r'Sector\sSizes:\s+(\d+)\D+(\d+)'             , 'SectorSizes' , None, False, lambda match: [int(match.group(1)), int(match.group(2))]),
        (r'Sector\sSize:\s+(\d+)'                      , 'SectorSizes' , None, False, lambda match: [int(match.group(1)), int(match.group(1))]),
        (r'5\s+Reallocated_Sector_Ct.*\s(\d+)$'        , 'ErrorCount'  ,    0,  True, lambda match: int(match.group(1))),
        (r'187\s+Reported_Uncorrec.*\s(\d+)$'          , 'ErrorCount'  ,    0,  True, lambda match: int(match.group(1))),
        (r'196\s+Reallocated_Event_Count.*\s(\d+)$'    , 'ErrorCount'  ,    0,  True, lambda match: int(match.group(1))),
        (r'197\s+Current_Pending_Sector.*\s(\d+)$'     , 'ErrorCount'  ,    0,  True, lambda match: int(match.group(1))),
        (r'198\s+Offline_Uncorrectable.*\s(\d+)$'      , 'ErrorCount'  ,    0,  True, lambda match: int(match.group(1))),
        # Common errors
        (r'Smartctl\sopen\sdevice.*No\ssuch\sdevice\sor\saddress', 'SMART', True, False, lambda match: False),
        (r'.*Terminate\scommand\searly\sdue'                     , 'Disk' , True, False, lambda match: False),
        # SCT Error correction
        (r'Read:\s+(\d+)\s', 'SCT_Read', None, False, lambda match: int(match.group(1)) / 10),
        (r'Write:\s+(\d+)\s', 'SCT_Write', None, False, lambda match: int(match.group(1)) /10)
    ]

    def __init__(self, options, device):
        if not os.path.isfile(smartctl):
            self.SMART = False
            return
        self._set_default_attributes()
        self.Technology = 'SATA'
        self.__cmd_smart = '{} {}'.format(options, device)
        self.__cmd_smart = '{} -x {}'.format(smartctl, self.__cmd_smart.strip())
        self.__cmd_scterc = '{} -l scterc {}'.format(smartctl, device)
        self.__load_values()
        if self.Technology == 'SATA':
            if self.PHYCount == 0:
                self.PHYCount = 1
        self.SCT = [self.SCT_Read, self.SCT_Write]

    def __load_values(self):
        for line in helpers.getOutput(self.__cmd_smart):
            if self._process_attributes_line(line):
                continue
            # SAS
            match = re.search(r'Product:\s+(\S.*)$', line)
            if match:
                self.Model = '{} {}'.format(self.Vendor, match.group(1)) if hasattr(self, 'Vendor') else match.group(1)
                continue
        for line in helpers.getOutput(self.__cmd_scterc):
            if self._process_attributes_line(line):
                continue
