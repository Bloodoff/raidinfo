import re

from . import helpers
from .mixins import TextAttributeParser

smartctl = "/usr/sbin/smartctl"


class SMARTinfo(TextAttributeParser):
    _attributes = [
        (r'Model\sFamily:\s+(.*)$'                     , 'Vendor'      , None, None),
        (r'Device\sModel:\s+(.*)$'                     , 'Model'       , None, None),
        (r'Serial\s[N|n]umber:\s+(.*)$'                , 'Serial'      , None, None),
        (r'Firmware\sVersion:\s+(.*)$'                 , 'Firmware'    , None, None),
        (r'User\sCapacity:.*\[(.*)\]$'                 , 'Capacity'    , None, None),
        (r'Rotation\sRate:\s+(\d+)'                    , 'RPM'         , None, None),
        (r'Form\sFactor:\s+(\S+)'                      , 'FormFactor'  , None, None),
        (r'SATA Version is:.+\s(\S+)\sGb\/s'           , 'PHYSpeed'    , None, None),
        (r'194\sTemperature_Celsius.*\s(\d+)(?:\s\(|$)', 'Temperature' , None, None),
        (r'9\sPower_On_Hours+.*\s(\d+)$'               , 'PowerOnHours', None, None),
        (r'Vendor:\s+(\S.*)$'                          , 'Vendor'      , None, None),
        (r'Revision:\s+(\S.*)$'                        , 'Firmware'    , None, None),
        (r'Current\sDrive\sTemperature:\s+(\d.*)'      , 'Temperature' , None, None),
        (r'number\sof\shours\spowered\sup\s=\s+(\d*)'  , 'PowerOnHours', None, None),
        (r'Sector\sSizes:\s+(\d+)\D+(\d+)'             , 'SectorSizes' , None, lambda match: [int(match.group(1)), int(match.group(2))]),
        (r'Sector\sSize:\s+(\d+)'                      , 'SectorSizes' , None, lambda match: [int(match.group(1)), int(match.group(1))]),
        (r'5\s+Reallocated_Sector_Ct.*\s(\d+)$'        , 'ErrorCount'  ,    0, lambda match: int(match.group(1))),
        (r'196\s+Reallocated_Event_Count.*\s(\d+)$'    , 'ErrorCount'  ,    0, lambda match: int(match.group(1))),
        (r'197\s+Current_Pending_Sector.*\s(\d+)$'     , 'ErrorCount'  ,    0, lambda match: int(match.group(1))),
        (r'198\s+Offline_Uncorrectable.*\s(\d+)$'      , 'ErrorCount'  ,    0, lambda match: int(match.group(1))),
        # Common errors
        (r'Smartctl\sopen\sdevice.*No\ssuch\sdevice\sor\saddress', 'SMART', True, lambda match: False),
        (r'.*Terminate\scommand\searly\sdue'                     , 'Disk' , True, lambda match: False)
    ]

    def __init__(self, options, device):
        self._set_default_attributes
        self.Technology = 'SATA'
        self.PHYCount = 1
        self.__cmd = '{} {}'.format(options, device)
        self.__cmd = '{} -x {}'.format(smartctl, self.__cmd.strip())
        self.__load_values()

    def __load_values(self):
        for line in helpers.getOutput(self.__cmd):
            if self._process_attributes_line(line):
                continue
            # SAS
            match = re.search(r'Product:\s+(\S.*)$', line)
            if match:
                self.Model = '{} {}'.format(self.Vendor, match.group(1)) if hasattr(self, 'Vendor') else match.group(1)
                continue
