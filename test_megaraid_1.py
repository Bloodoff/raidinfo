#!/usr/bin/python3
import os
import re
import pytest
import mock

from lib import *

FakeResponses = {
    '/opt/MegaRAID/storcli/storcli64 show nolog': 'testdata/megaraid-1/util-1.txt',
    '/opt/MegaRAID/storcli/storcli64 /c0 show all nolog': 'testdata/megaraid-1/util-2.txt',
    '/opt/MegaRAID/storcli/storcli64 /c0/v0 show all nolog': 'testdata/megaraid-1/util-3.txt',
    '/opt/MegaRAID/storcli/storcli64 /c0/e252/s5 show all nolog': 'testdata/megaraid-1/util-4.txt',
    '/opt/MegaRAID/storcli/storcli64 /c0/e252/s2 show all nolog': 'testdata/megaraid-1/util-5.txt',
    '/opt/MegaRAID/storcli/storcli64 /c0/e252/s3 show all nolog': 'testdata/megaraid-1/util-6.txt',
    '/opt/MegaRAID/storcli/storcli64 /c0/e252/s6 show all nolog': 'testdata/megaraid-1/util-7.txt',
    '/opt/MegaRAID/storcli/storcli64 /c0/e252/s7 show all nolog': 'testdata/megaraid-1/util-8.txt',
    '/opt/MegaRAID/storcli/storcli64 /c0/e253/s4 show all nolog': 'testdata/megaraid-1/util-9.txt',
    '/opt/MegaRAID/storcli/storcli64 /c0/e253/s6 show all nolog': 'testdata/megaraid-1/util-10.txt',
    '/opt/MegaRAID/storcli/storcli64 /c0/e253/s7 show all nolog': 'testdata/megaraid-1/util-11.txt',
    '/opt/MegaRAID/storcli/storcli64 /c0/e253/s0 show all nolog': 'testdata/megaraid-1/util-12.txt',
    '/opt/MegaRAID/storcli/storcli64 /c0/e253/s1 show all nolog': 'testdata/megaraid-1/util-13.txt',
    '/opt/MegaRAID/storcli/storcli64 /c0/e253/s2 show all nolog': 'testdata/megaraid-1/util-14.txt',
    '/opt/MegaRAID/storcli/storcli64 /c0/e253/s5 show all nolog': 'testdata/megaraid-1/util-15.txt',
    '/opt/MegaRAID/storcli/storcli64 /c0/e253/s3 show all nolog': 'testdata/megaraid-1/util-16.txt',
    '/usr/sbin/smartctl -x -d megaraid,41 /dev/disk/by-id/scsi-3600605b001a02e401f57fe47e983aa9a': 'testdata/megaraid-1/smart/smart-1.txt',
    '/usr/sbin/smartctl -x -d megaraid,42 /dev/disk/by-id/scsi-3600605b001a02e401f57fe47e983aa9a': 'testdata/megaraid-1/smart/smart-2.txt',
    '/usr/sbin/smartctl -x -d megaraid,43 /dev/disk/by-id/scsi-3600605b001a02e401f57fe47e983aa9a': 'testdata/megaraid-1/smart/smart-3.txt',
    '/usr/sbin/smartctl -x -d megaraid,44 /dev/disk/by-id/scsi-3600605b001a02e401f57fe47e983aa9a': 'testdata/megaraid-1/smart/smart-4.txt',
    '/usr/sbin/smartctl -x -d megaraid,45 /dev/disk/by-id/scsi-3600605b001a02e401f57fe47e983aa9a': 'testdata/megaraid-1/smart/smart-5.txt',
    '/usr/sbin/smartctl -x -d megaraid,46 /dev/disk/by-id/scsi-3600605b001a02e401f57fe47e983aa9a': 'testdata/megaraid-1/smart/smart-6.txt',
    '/usr/sbin/smartctl -x -d megaraid,47 /dev/disk/by-id/scsi-3600605b001a02e401f57fe47e983aa9a': 'testdata/megaraid-1/smart/smart-7.txt',
    '/usr/sbin/smartctl -x -d megaraid,48 /dev/disk/by-id/scsi-3600605b001a02e401f57fe47e983aa9a': 'testdata/megaraid-1/smart/smart-8.txt',
    '/usr/sbin/smartctl -x -d megaraid,49 /dev/disk/by-id/scsi-3600605b001a02e401f57fe47e983aa9a': 'testdata/megaraid-1/smart/smart-9.txt',
    '/usr/sbin/smartctl -x -d megaraid,50 /dev/disk/by-id/scsi-3600605b001a02e401f57fe47e983aa9a': 'testdata/megaraid-1/smart/smart-10.txt',
    '/usr/sbin/smartctl -x -d megaraid,51 /dev/disk/by-id/scsi-3600605b001a02e401f57fe47e983aa9a': 'testdata/megaraid-1/smart/smart-11.txt',
    '/usr/sbin/smartctl -x -d megaraid,52 /dev/disk/by-id/scsi-3600605b001a02e401f57fe47e983aa9a': 'testdata/megaraid-1/smart/smart-12.txt',
    '/usr/sbin/smartctl -x -d megaraid,53 /dev/disk/by-id/scsi-3600605b001a02e401f57fe47e983aa9a': 'testdata/megaraid-1/smart/smart-13.txt',
    '/usr/sbin/smartctl -l scterc -d megaraid,41 /dev/disk/by-id/scsi-3600605b001a02e401f57fe47e983aa9a': 'testdata/megaraid-1/smart/smart-sct.txt',
    '/usr/sbin/smartctl -l scterc -d megaraid,42 /dev/disk/by-id/scsi-3600605b001a02e401f57fe47e983aa9a': 'testdata/megaraid-1/smart/smart-sct.txt',
    '/usr/sbin/smartctl -l scterc -d megaraid,43 /dev/disk/by-id/scsi-3600605b001a02e401f57fe47e983aa9a': 'testdata/megaraid-1/smart/smart-sct.txt',
    '/usr/sbin/smartctl -l scterc -d megaraid,44 /dev/disk/by-id/scsi-3600605b001a02e401f57fe47e983aa9a': 'testdata/megaraid-1/smart/smart-sct.txt',
    '/usr/sbin/smartctl -l scterc -d megaraid,45 /dev/disk/by-id/scsi-3600605b001a02e401f57fe47e983aa9a': 'testdata/megaraid-1/smart/smart-sct.txt',
    '/usr/sbin/smartctl -l scterc -d megaraid,46 /dev/disk/by-id/scsi-3600605b001a02e401f57fe47e983aa9a': 'testdata/megaraid-1/smart/smart-sct.txt',
    '/usr/sbin/smartctl -l scterc -d megaraid,47 /dev/disk/by-id/scsi-3600605b001a02e401f57fe47e983aa9a': 'testdata/megaraid-1/smart/smart-sct.txt',
    '/usr/sbin/smartctl -l scterc -d megaraid,48 /dev/disk/by-id/scsi-3600605b001a02e401f57fe47e983aa9a': 'testdata/megaraid-1/smart/smart-sct.txt',
    '/usr/sbin/smartctl -l scterc -d megaraid,49 /dev/disk/by-id/scsi-3600605b001a02e401f57fe47e983aa9a': 'testdata/megaraid-1/smart/smart-sct.txt',
    '/usr/sbin/smartctl -l scterc -d megaraid,50 /dev/disk/by-id/scsi-3600605b001a02e401f57fe47e983aa9a': 'testdata/megaraid-1/smart/smart-sct.txt',
    '/usr/sbin/smartctl -l scterc -d megaraid,51 /dev/disk/by-id/scsi-3600605b001a02e401f57fe47e983aa9a': 'testdata/megaraid-1/smart/smart-sct.txt',
    '/usr/sbin/smartctl -l scterc -d megaraid,52 /dev/disk/by-id/scsi-3600605b001a02e401f57fe47e983aa9a': 'testdata/megaraid-1/smart/smart-sct.txt',
    '/usr/sbin/smartctl -l scterc -d megaraid,53 /dev/disk/by-id/scsi-3600605b001a02e401f57fe47e983aa9a': 'testdata/megaraid-1/smart/smart-sct.txt',
}


def read_file(filename):
    file = open(filename)
    return [line.strip() for line in file]


def fake_isfile(filename):
    if filename in ['/opt/MegaRAID/storcli/storcli64', '/usr/sbin/smartctl']:
        return True
    return False

__original_listdir = os.listdir


def fake_listdir(dir):
    return __original_listdir('testdata/megaraid-1{}'.format(dir))


def fake_getOutput(cmd):
    lines = []
    testfile = FakeResponses.get(cmd, False)
    if not testfile:
        raise Exception('Test file for command "{}" not found'.format(cmd))
    output = read_file('{}/{}'.format(os.path.dirname(__file__), testfile))
    for line in output:
        if not re.match(r'^$', line.strip()):
            lines.append(line.strip())
    return lines


@mock.patch('os.listdir', fake_listdir)
@mock.patch('os.path.isfile', fake_isfile)
@mock.patch('lib.helpers.getOutput', fake_getOutput)
def test_megaraid_1(monkeypatch):
    controllers = raid.RaidController.probe()
    for controller in controllers:
        controller.printInfo()
