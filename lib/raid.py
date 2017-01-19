class raidController(object):
    def __init__(self, name):
        self.Name = name
        self.LDs = []

    # Searches for raid controllers of all technology 
    @staticmethod
    def probe():
        controllers = []
        for technology in raidController.__subclasses__():
            names = technology.probe()
            if names:
                for name in names:
                    controllers.append(technology(name))
        return controllers

    def printInfo(self):
        print ''
        print 'Controller {} type {} contains {} logical drives'.format(self.Name, self.Type, len(self.LDs))
        self.printSpecificInfo()
        for LD in self.LDs:
            LD.printInfo()

    def printSpecificInfo(self):
        pass            

class raidLD(object):
    
    def __init__(self, name, controller):
        self.Name = name
        self.Controller = controller
        self.PDs = []

    def printInfo(self):
        print ''
        print 'Device: {}, {}, {}, {}'.format(self.Device, self.Size, self.Level, self.State)
        self.printSpecificInfo()
        
        print ''
        print 'Active disks: {} of {}'.format(self.DriveActiveCount, self.DriveCount)
        raidPD.printTitle()
        for PD in self.PDs:
            PD.printInfo()

    def printSpecificInfo(self):
        pass

class raidPD(object):

    def __init__(self, name, ld):
        self.LD = ld
        self.Name=name
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
        self.Speed = '-'
        self.Tempreature = '-'
        self.PowerOnHours = '-'
        self.BadSectorsCount = '-'

    @staticmethod
    def printTitle():
        print 'Device       |Slot| State      | Tech | Model                    | Serial number    | Firmware | Capacity   | Sector size |  FF  |  RPM  | Speed     | Temp | Hours  | Errors'
        print '-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------'

    def printInfo(self):
        print '{:12} | {:>2} | {:10} | {:4} | {:24} | {:16} | {:8} | {:>10} | {:>4} / {:>4} | {:3}" | {:>5} | {:>4} Gbps | {:>4} | {:>6} | {:>6}'.format(
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
            self.Speed,
            self.Tempreature,
            self.PowerOnHours,
            self.BadSectorsCount
        )
