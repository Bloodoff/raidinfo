import re

from . import helpers

smartctl = "/usr/sbin/smartctl"


class SMARTinfo(object):
    def __init__(self, options, device):
        self.SMART = True
        self.ErrorCount = 0
        self.Technology = 'SATA'
        self.PHYCount = 1
        self.__cmd = '{} {}'.format(options, device)
        self.__cmd = '{} -x {}'.format(smartctl, self.__cmd.strip())
        self.__load_values()

    def __load_values(self):
        for line in helpers.getOutput(self.__cmd):
            match = re.search(r'Model\sFamily:\s+(.*)$', line)
            if match:
                self.Vendor = match.group(1)
            match = re.search(r'Device\sModel:\s+(.*)$', line)
            if match:
                self.Model = match.group(1)
            match = re.search(r'Serial\sNumber:\s+(.*)$', line)
            if match:
                self.Serial = match.group(1)
            match = re.search(r'Firmware\sVersion:\s+(.*)$', line)
            if match:
                self.Firmware = match.group(1)
            match = re.search(r'User\sCapacity:.*\[(.*)\]$', line)
            if match:
                self.Capacity = match.group(1)
            match = re.search(r'Sector\sSizes:\s+(\d+)\D+(\d+)', line)
            if match:
                self.SectorSizes = [match.group(1), match.group(2)]
            match = re.search(r'Rotation\sRate:\s+(\d+)', line)
            if match:
                self.RPM = match.group(1)
            match = re.search(r'Form\sFactor:\s+(\S+)', line)
            if match:
                self.FormFactor = match.group(1)
            match = re.search(r'SATA Version is:.+current:\s(\S+)', line)
            if match:
                self.PHYSpeed = match.group(1)
            for item in [
                    r'5\s+Reallocated_Sector_Ct.*\s(\d+)$',
                    r'196\s+Reallocated_Event_Count.*\s(\d+)$',
                    r'197\s+Current_Pending_Sector.*\s(\d+)$',
                    r'198\s+Offline_Uncorrectable.*\s(\d+)$'
            ]:
                match = re.search(item, line)
                if match:
                    self.ErrorCount = self.ErrorCount + int(match.group(1))
            match = re.search(r'194\sTemperature_Celsius.*\s(\d+)(?:\s\(|$)', line)
            if match:
                self.Temperature = match.group(1)
            match = re.search(r'9\sPower_On_Hours+.*\s(\d+)$', line)
            if match:
                self.PowerOnHours = match.group(1)

            match = re.search(r'Smartctl\sopen\sdevice.*No\ssuch\sdevice\sor\saddress', line)
            if match:
                self.SMART = False
            match = re.search(r'.*Terminate\scommand\searly\sdue', line)
            if match:
                self.SMART = False
