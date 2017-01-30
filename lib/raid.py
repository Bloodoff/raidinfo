import re


class DeviceCapacity(object):
    UNITS = {-1: 'unknown', 0: 'bytes', 1: 'KiB', 2: 'MiB', 3: 'GiB', 4: 'TiB'}

    def __init__(self, capacity, units=None):
        self.PassedValue = capacity
        if units is None:
            self.Units = -1
            return
        self.Value = int(re.sub(r'\D', '', str(capacity)))
        for key, unit in self.UNITS.items():
            if units.lower() == unit.lower():
                self.Units = key
                break
        while self._upUnit():
            pass

    def _upUnit(self):
        if self.Value < 1024:
            return False
        if self.Units == 4:
            return False
        self.Value = self.Value / 1024
        self.Units = self.Units + 1
        return True

    def __str__(self):
        if self.Units == -1:
            return self.PassedValue
        return '{} {}'.format(round(self.Value, 2), self.UNITS[self.Units])


class RaidController(object):
    def __init__(self, name):
        self.Name = name.strip()
        self.LDs = []

    # Searches for raid controllers of all technology
    @staticmethod
    def probe():
        controllers = []
        for technology in RaidController.__subclasses__():
            names = technology.probe()
            if names:
                for name in names:
                    controllers.append(technology(name))
        return controllers

    def printInfo(self):
        print('')
        print('Controller {} type {} contains {} logical drives'.format(self.Name, self.Type, len(self.LDs)))
        self.printSpecificInfo()
        for LD in self.LDs:
            LD.printInfo()

    def printSpecificInfo(self):
        pass


class RaidLD(object):

    def __init__(self, name, controller):
        self.Name = name
        self.Controller = controller
        self.PDs = []

    def printInfo(self):
        print('')
        print('Device: {}, {}, {}, {}'.format(self.Device, self.Size, self.Level, self.State))
        self.printSpecificInfo()

        print('')
        print('Active disks: {} of {}'.format(self.DriveActiveCount, self.DriveCount))
        RaidPD.printTitle()
        for PD in self.PDs:
            PD.printInfo()

    def printSpecificInfo(self):
        pass


class RaidPD(object):
    # Printed fields
    __fields = [
        ('Device', 9, '>', '-', 'Device', None),
        ('Slot', 4, '>', '-', 'Slot', None),
        ('State', 10, '>', '-', 'State', None),
        ('Tech', 4, '>', '-', 'Technology', None),
        ('Model', 24, '>', '-', 'Model', None),
        ('Serial number', 20, '>', '-', 'Serial', None),
        ('Firmware', 10, '>', '-', 'Firmware', None),
        ('Capacity', 10, '>', '-', 'Capacity', None),
        ('Sector size', 11, '>', ['-', '-'], 'SectorSizes', lambda value: '{}/{}'.format(value[0], value[1])),
        ('FF', 3, '>', '-', 'FormFactor', None),
        ('RPM', 6, '>', '-', 'RPM', None),
        ('PHY', 6, '>', None, 'PHYSpeed', '_formatPHYInfo'),
        ('Temp', 4, '>', '-', 'Temperature', None),
        ('Hours', 6, '>', '-', 'PowerOnHours', None),
        ('Errors', 6, '>', '-', 'ErrorCount', None)
    ]

    def __init__(self, name, ld):
        self.LD = ld
        self.Name = name

    @staticmethod
    def printTitle():
        line_elements = []
        for title, lenght, align, _, _, _ in RaidPD.__fields:
            line_elements.append('{!s:{}{}}'.format(title, align, lenght))
        titleline = ' |'.join(line_elements)
        print(titleline)
        print('-' * len(titleline))

    def _formatPHYInfo(self):
        if not hasattr(self, 'PHYCount'):
            return '-'
        return '{!s:1}x{}'.format(self.PHYCount, self.PHYSpeed)

    def printInfo(self):
        line_elements = []
        for title, lenght, align, default, attr, format_func in RaidPD.__fields:
            value = getattr(self, attr) if hasattr(self, attr) else default
            if format_func is not None:
                value = format_func(value) if callable(format_func) else getattr(self, format_func)()
            line_elements.append('{!s:{}{}}'.format(value, align, lenght))
        print(' |'.join(line_elements))
