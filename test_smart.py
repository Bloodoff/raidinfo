#!/usr/bin/python3
import os
import re
import pytest
import mock

from lib import *
from lib.smart import SMARTinfo


FakeResponses = { '/usr/sbin/smartctl -x /dev/sda': 'testdata/smart/smart-1.txt',
                  '/usr/sbin/smartctl -x /dev/sdb': 'testdata/smart/smart-2.txt',
                  }


def read_file(filename):
    file = open(filename)
    return [line.strip() for line in file]

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


@mock.patch('lib.helpers.getOutput', fake_getOutput)
def test_smart_1(monkeypatch):
    smart = SMARTinfo('', '/dev/sda')
    assert smart.SectorSizes == [512, 512] 
    

@mock.patch('lib.helpers.getOutput', fake_getOutput)
def test_smart_2(monkeypatch):
    smart = SMARTinfo('', '/dev/sdb')
    assert smart.SectorSizes == [512, 4096] 
    
    