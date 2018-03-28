import os
import re

from . import helpers

from .raid import RaidController, RaidLD, RaidPD, DeviceCapacity
from .smart import SMARTinfo

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
        self.Rebuild = self.__getLDrebuild()
        self.MismatchCount = self.__getLDmismatchCount()
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
        if (self.Rebuild < 100):
            print('Rebuild progress: {}%'.format(self.Rebuild))
        print('Metadata version: {}, layout {}'.format(self.Version, self.Layout))
        if (self.MismatchCount > 0):
            print('Warning, found {} mismathed blocks!!!'.format(self.MismatchCount))

    def __getLDmismatchCount(self):
        return int(helpers.readFile('{}/{}/md/mismatch_cnt'.format(syspath, self.Name)))

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

    def __getLDrebuild(self):
        rebuild = helpers.readFile('{}/{}/md/sync_completed'.format(syspath, self.Name))
        if (rebuild == 'none'):
            return 100
        elif (rebuild == 'delayed'):
            return 0
        else:
            temp = rebuild.split(' / ')
            return int(int(temp[0]) * 100 / int(temp[1]))

    def __getLDsize(self):
        blockcount = int(helpers.readFile('{}/{}/size'.format(syspath, self.Name)))
        blocksize = int(helpers.readFile('{}/{}/queue/logical_block_size'.format(syspath, self.Name)))
        return DeviceCapacity(round(blockcount / 1024 * blocksize), 'KiB')

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
        smart = SMARTinfo('', self.PhysicalDevice)
        for prop in ['Model', 'Serial', 'Firmware', 'Capacity', 'SectorSizes', 'FormFactor', 'PHYCount', 'PHYSpeed', 'RPM', 'PowerOnHours', 'ErrorCount', 'Temperature', 'SCT']:
            if hasattr(smart, prop):
                setattr(self, prop, getattr(smart, prop))

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
