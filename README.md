# Raidinfo [![Build Status](https://travis-ci.org/Bloodoff/raidinfo.svg?branch=master)](https://travis-ci.org/Bloodoff/raidinfo)
Scripts for generating compact reports for RAID controllers, for now it's only basic support, for extending need more outputs of verndor raid utilities

Supported:
* Linux SoftRAID
* 3Ware (such as 9690SA)
* HP SmartArray

Sample output:
```
Controller 0 type Soft contains 3 logical drives

Device: /dev/md126, 64 GiB, RAID1, Optimal
Metadata version: 1.2, layout not applicable

Active disks: 2 of 4
Device       |Slot| State      | Tech | Model                    | Serial number        | Firmware | Capacity   | Sector size | F F |  RPM  | PHY Speed | Temp | Hours  | Errors
--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
/dev/sdd3    |  - | Hot Spare  | SATA | TOSHIBA HDWE160          | 26LAK44RF56D         | FS2A     |    6.00 TB |  512 / 4096 | 3.5 |  7200 |   1 x 3.0 |   41 |   3747 |      0
/dev/sda3    |  1 | Optimal    | SATA | TOSHIBA HDWE160          | 26P9K3DHF56D         | FS2A     |    6.00 TB |  512 / 4096 | 3.5 |  7200 |   1 x 3.0 |   38 |   3816 |      0
/dev/sdc3    |  - | Hot Spare  | SATA | TOSHIBA HDWE160          | 26PBK24NF56D         | FS2A     |    6.00 TB |  512 / 4096 | 3.5 |  7200 |   1 x 3.0 |   43 |   3747 |      0
/dev/sdb3    |  0 | Optimal    | SATA | TOSHIBA HDWE160          | 26P9K3DGF56D         | FS2A     |    6.00 TB |  512 / 4096 | 3.5 |  7200 |   1 x 3.0 |   41 |   3816 |      0

Device: /dev/md122, 11 TiB, RAID6, Optimal
Metadata version: 1.2, layout left-symmetric

Active disks: 4 of 4
Device       |Slot| State      | Tech | Model                    | Serial number        | Firmware | Capacity   | Sector size | F F |  RPM  | PHY Speed | Temp | Hours  | Errors
--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
/dev/sda4    |  0 | Optimal    | SATA | TOSHIBA HDWE160          | 26P9K3DHF56D         | FS2A     |    6.00 TB |  512 / 4096 | 3.5 |  7200 |   1 x 3.0 |   38 |   3816 |      0
/dev/sdd4    |  3 | Optimal    | SATA | TOSHIBA HDWE160          | 26LAK44RF56D         | FS2A     |    6.00 TB |  512 / 4096 | 3.5 |  7200 |   1 x 3.0 |   41 |   3747 |      0
/dev/sdb4    |  0 | Optimal    | SATA | TOSHIBA HDWE160          | 26P9K3DGF56D         | FS2A     |    6.00 TB |  512 / 4096 | 3.5 |  7200 |   1 x 3.0 |   41 |   3816 |      0
/dev/sdc4    |  2 | Optimal    | SATA | TOSHIBA HDWE160          | 26PBK24NF56D         | FS2A     |    6.00 TB |  512 / 4096 | 3.5 |  7200 |   1 x 3.0 |   43 |   3747 |      0

Device: /dev/md127, 501 MiB, RAID1, Optimal
Metadata version: 1.2, layout not applicable

Active disks: 2 of 4
Device       |Slot| State      | Tech | Model                    | Serial number        | Firmware | Capacity   | Sector size | F F |  RPM  | PHY Speed | Temp | Hours  | Errors
--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
/dev/sdd2    |  - | Hot Spare  | SATA | TOSHIBA HDWE160          | 26LAK44RF56D         | FS2A     |    6.00 TB |  512 / 4096 | 3.5 |  7200 |   1 x 3.0 |   41 |   3747 |      0
/dev/sdb2    |  0 | Optimal    | SATA | TOSHIBA HDWE160          | 26P9K3DGF56D         | FS2A     |    6.00 TB |  512 / 4096 | 3.5 |  7200 |   1 x 3.0 |   41 |   3816 |      0
/dev/sda2    |  1 | Optimal    | SATA | TOSHIBA HDWE160          | 26P9K3DHF56D         | FS2A     |    6.00 TB |  512 / 4096 | 3.5 |  7200 |   1 x 3.0 |   38 |   3816 |      0
/dev/sdc2    |  - | Hot Spare  | SATA | TOSHIBA HDWE160          | 26PBK24NF56D         | FS2A     |    6.00 TB |  512 / 4096 | 3.5 |  7200 |   1 x 3.0 |   43 |   3747 |      0
```
