import os
import re

import helpers

from raid import RaidController, RaidLD, RaidPD


syspath = "/sys/block"
mdstat = "/proc/mdstat"
devpath = "/dev"
smartctl = "/usr/sbin/smartctl"


class RaidControllerSoft(RaidController):

    def __init__(self, name):
        super(self.__class__, self).__init__(name)
        self.Type = 'Soft'
        self.__enumerateLD()

    @staticmethod
    def probe():
        if not os.path.isfile(mdstat):
            return False
        return '0'

    def __enumerateLD(self):
        output = helpers.readFile(mdstat)

        for line in output:
            match = re.search(r'(md\d+)\s:', line)
            if match:
                self.LDs.append(RaidLDsoft(match.group(1), self))


class RaidLDsoft(RaidLD):
    def __init__(self, name, controller):
        super(self.__class__, self).__init__(name, controller)

        self.Device = '/dev/{}'.format(self.Name)
        self.Level = self.__getLDlevel()
        self.Layout = self.__getLDlayout()
        self.State = self.__getLDstate()
        self.Version = self.__getLDmeta()
        self.DriveActiveCount = self.__getLDdriveCount()
        self.Size = self.__getLDsize()
        self.__enumeratePD()

    def __enumeratePD(self):
        path = '{}/{}/md'.format(syspath, self.Name)

        for filename in [
                f for f in os.listdir(path)
                if os.path.isdir(os.path.join(path, f))]:
            match = re.search(r'dev-(.+)', filename)
            if match:
                self.PDs.append(RaidPDsoft(match.group(1), self))
        self.DriveCount = len(self.PDs)

    def printSpecificInfo(self):
        print 'Metadata version: {}, layout {}'.format(self.Version, self.Layout)

    def __getLDlevel(self):
        return helpers.readFile('{}/{}/md/level'.format(syspath, self.Name)).upper()

    def __getLDlayout(self):
        layout = int(helpers.readFile('{}/{}/md/layout'.format(syspath, self.Name)))
        return {
            0: 'not applicable',
            1: 'right-symmetric',
            2: 'left-symmetric'
        }.get(layout, layout)

    def __getLDmeta(self):
        return helpers.readFile('{}/{}/md/metadata_version'.format(syspath, self.Name))

    def __getLDstate(self):
        degraded = int(helpers.readFile('{}/{}/md/degraded'.format(syspath, self.Name)))
        return {
            0: 'Optimal',
            1: 'Degraded'
        }.get(degraded, degraded)

    def __getLDsize(self):
        blockcount = int(helpers.readFile('{}/{}/size'.format(syspath, self.Name)))
        blocksize = int(helpers.readFile('{}/{}/queue/logical_block_size'.format(syspath, self.Name)))
        size = blockcount / 1024 * blocksize / 1024
        if size < 1024:
            return '{} MiB'.format(size)
        size = size / 1024
        if size < 1024:
            return '{} GiB'.format(size)
        size = size / 1024
        return '{} TiB'.format(size)

    def __getLDdriveCount(self):
        return helpers.readFile('{}/{}/md/raid_disks'.format(syspath, self.Name))


class RaidPDsoft(RaidPD):

    def __init__(self, name, ld):
        super(self.__class__, self).__init__(name, ld)

        self.Device = '{}/{}'.format(devpath, self.Name)
        match = re.search(r'(\D+)', self.Device)
        self.PhysicalDevice = match.group(1)
        self.Technology = 'SATA'
        self.Slot = self.__getSlot()
        self.State = self.__getState()
        self.Model = self.__getModel()
        self.Serial = self.__getSerial()
        self.Firmware = self.__getFirmware()
        self.Capacity = self.__getCapacity()
        self.SectorSizes = self.__getSectorSizes()
        self.FormFactor = self.__getFormFactor()
        self.Speed = self.__getSpeed()
        self.RPM = self.__getRPM()
        self.PowerOnHours = self.__getPowerOnHours()
        self.BadSectorsCount = self.__getBadSectorsCount()
        self.Tempreature = self.__getTemperature()

    def __getSlot(self):
        slot = helpers.readFile('{}/{}/md/dev-{}/slot'.format(syspath, self.LD.Name, self.Name))
        if slot == 'none':
            return '-'
        return slot

    def __getState(self):
        state = helpers.readFile('{}/{}/md/dev-{}/state'.format(syspath, self.LD.Name, self.Name))
        return {
            'in_sync': 'Optimal',
            'spare': 'Hot Spare',
            'faulty': 'Faulty'
        }.get(state, state)

    def __getModel(self):
        for line in helpers.getOutput('{} -a {}'.format(smartctl, self.PhysicalDevice)):
            match = re.search(r'Device Model:\s+(.*)$', line)
            if match:
                return match.group(1)
        return '-'

    def __getSerial(self):
        for line in helpers.getOutput('{} -a {}'.format(smartctl, self.PhysicalDevice)):
            match = re.search(r'Serial Number:\s+(.*)$', line)
            if match:
                return match.group(1)
        return '-'

    def __getFirmware(self):
        for line in helpers.getOutput('{} -a {}'.format(smartctl, self.PhysicalDevice)):
            match = re.search(r'Firmware Version:\s+(.*)$', line)
            if match:
                return match.group(1)
        return '-'

    def __getCapacity(self):
        for line in helpers.getOutput('{} -a {}'.format(smartctl, self.PhysicalDevice)):
            match = re.search(r'User Capacity:.+\[(.*)\]$', line)
            if match:
                return match.group(1)
        return 0

    def __getSectorSizes(self):
        for line in helpers.getOutput('{} -a {}'.format(smartctl, self.PhysicalDevice)):
            match = re.search(r'Sector Sizes:\s+(\d+)\D+(\d+)', line)
            if match:
                return [match.group(1), match.group(2)]
        return [0, 0]

    def __getRPM(self):
        for line in helpers.getOutput('{} -a {}'.format(smartctl, self.PhysicalDevice)):
            match = re.search(r'Rotation Rate:\s+(\d+)', line)
            if match:
                return match.group(1)
        return 0

    def __getFormFactor(self):
        for line in helpers.getOutput('{} -a {}'.format(smartctl, self.PhysicalDevice)):
            match = re.search(r'Form Factor:\s+(.+)\s+inches', line)
            if match:
                return match.group(1)
        return '-'

    def __getSpeed(self):
        for line in helpers.getOutput('{} -a {}'.format(smartctl, self.PhysicalDevice)):
            match = re.search(r'SATA Version is:.+current:\s(.+)\sGb/s\)', line)
            if match:
                return match.group(1)
        return '-'

    def __getPowerOnHours(self):
        for line in helpers.getOutput('{} -a {}'.format(smartctl, self.PhysicalDevice)):
            match = re.search(r'9\s+Power_On_Hours.*\s(\d+)$', line)
            if match:
                return match.group(1)
        return 0

    def __getBadSectorsCount(self):
        count = 0
        for line in helpers.getOutput('{} -a {}'.format(smartctl, self.PhysicalDevice)):
            for item in [
                    r'5\s+Reallocated_Sector_Ct.*\s(\d+)$',
                    r'196\s+Reallocated_Event_Count.*\s(\d+)$',
                    r'197\s+Current_Pending_Sector.*\s(\d+)$',
                    r'198\s+Offline_Uncorrectable.*\s(\d+)$'
            ]:
                match = re.search(item, line)
                if match:
                    count = count + int(match.group(1))
        return count

    def __getTemperature(self):
        for line in helpers.getOutput('{} -a {}'.format(smartctl, self.PhysicalDevice)):
            match = re.search(r'194\sTemperature_Celsius.*\s(\d+)(?:\s\(|$)', line)
            if match:
                return match.group(1)
        return '-'
