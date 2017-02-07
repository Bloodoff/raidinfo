#!/usr/bin/python3
import os
import re
import pytest
import mock

from lib import *

FakeResponses = {
    '/opt/MegaRAID/storcli/storcli64 show': 'testdata/megaraid-1/util-1.txt',
    '/opt/MegaRAID/storcli/storcli64 /c0 show all': 'testdata/megaraid-1/util-2.txt',
    '/opt/MegaRAID/storcli/storcli64 /c0/v0 show all': 'testdata/megaraid-1/util-3.txt',
    '/opt/MegaRAID/storcli/storcli64 /c0/e252/s5 show all': 'testdata/megaraid-1/util-4.txt',
    '/opt/MegaRAID/storcli/storcli64 /c0/e252/s2 show all': 'testdata/megaraid-1/util-4.txt',
    '/opt/MegaRAID/storcli/storcli64 /c0/e252/s3 show all': 'testdata/megaraid-1/util-4.txt',
    '/opt/MegaRAID/storcli/storcli64 /c0/e252/s6 show all': 'testdata/megaraid-1/util-4.txt',
    '/opt/MegaRAID/storcli/storcli64 /c0/e252/s7 show all': 'testdata/megaraid-1/util-4.txt',
    '/opt/MegaRAID/storcli/storcli64 /c0/e253/s4 show all': 'testdata/megaraid-1/util-4.txt',
    '/opt/MegaRAID/storcli/storcli64 /c0/e253/s6 show all': 'testdata/megaraid-1/util-4.txt',
    '/opt/MegaRAID/storcli/storcli64 /c0/e253/s7 show all': 'testdata/megaraid-1/util-4.txt',
    '/opt/MegaRAID/storcli/storcli64 /c0/e253/s0 show all': 'testdata/megaraid-1/util-4.txt',
    '/opt/MegaRAID/storcli/storcli64 /c0/e253/s1 show all': 'testdata/megaraid-1/util-4.txt',
    '/opt/MegaRAID/storcli/storcli64 /c0/e253/s2 show all': 'testdata/megaraid-1/util-4.txt',
    '/opt/MegaRAID/storcli/storcli64 /c0/e253/s5 show all': 'testdata/megaraid-1/util-4.txt',
    '/opt/MegaRAID/storcli/storcli64 /c0/e253/s3 show all': 'testdata/megaraid-1/util-4.txt',
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
