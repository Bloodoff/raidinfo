#!/usr/bin/python3
import os
import re
import pytest
import mock
import lib.helpers

from lib.raid import RaidController
from lib.raid_3ware import RaidController3ware


FakeResponses = { '/u1sr/sbin/tw_cli show'           : 'testdata/3ware/1.txt',
                  '/usr/sbin/tw_cli /c6 show'       : 'testdata/3ware/2.txt',
                  '/usr/sbin/tw_cli /c6/u0 show all': 'testdata/3ware/3.txt',
                  '/usr/sbin/tw_cli /c6/p0 show all': 'testdata/3ware/4.txt',
                  '/usr/sbin/tw_cli /c6/p1 show all': 'testdata/3ware/5.txt',
                  '/usr/sbin/tw_cli /c6 show all'   : 'testdata/3ware/6.txt'
                  }

def read_file(filename):
    file = open(filename)
    return [line.strip() for line in file]

def fake_getOutput(cmd):
    lines = []
    testfile = FakeResponses.get(cmd, False)
    if not testfile:
        print('Test file for command "{}" not found'.format(cmd))
    output = read_file('{}/{}'.format(os.path.dirname(__file__), testfile))
    for line in output:
        if not re.match(r'^$', line.strip()):
            lines.append(line.strip())
    return lines

@mock.patch('os.path.isfile', return_value=True)
@mock.patch('lib.helpers.getOutput', fake_getOutput)

def test_3ware_1(mock_1):
    controllers = RaidController.probe()
    for controller in controllers:
        controller.printInfo()
