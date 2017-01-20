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

    def __init__(self, name, ld):
        self.LD = ld
        self.Name = name
        # Set default values
        self.Device = '-'
        self.Slot = '-'
        self.State = '-'
        self.Technology = '-'
        self.Model = '-'
        self.Serial = '-'
        self.Firmware = '-'
        self.Capacity = '-'
        self.SectorSizes = []
        self.SectorSizes.append('-')
        self.SectorSizes.append('-')
        self.FormFactor = '-'
        self.PHYCount = 0
        self.PHYSpeed = None
        self.RPM = '-'
        self.Temperature = '-'
        self.PowerOnHours = '-'
        self.ErrorCount = '-'

    @staticmethod
    def printTitle():
        print('Device       |Slot| State      | Tech | Model                    | Serial number        | Firmware | Capacity   | Sector size | F F |  RPM  | PHY Speed | Temp | Hours  | Errors')
        print('--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')

    def printInfo(self):
        phy = '-'
        if (self.PHYCount > 0) and (self.PHYSpeed is not None):
            phy = '{} x {}'.format(self.PHYCount, self.PHYSpeed)
        print('{!s:12} | {!s:>2} | {!s:10} | {!s:4} | {!s:24} | {!s:20} | {!s:8} | {!s:>10} | {!s:>4} / {!s:>4} | {!s:3} | {!s:>5} | {!s:>9} | {!s:>4} | {!s:>6} | {!s:>6}'.format(
            self.Device,
            self.Slot,
            self.State,
            self.Technology,
            self.Model,
            self.Serial,
            self.Firmware,
            self.Capacity,
            self.SectorSizes[0],
            self.SectorSizes[1],
            self.FormFactor,
            self.RPM,
            phy,
            self.Temperature,
            self.PowerOnHours,
            self.ErrorCount
        ))
