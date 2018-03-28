#!/usr/bin/python3
import os
import re
import pytest
import mock

from lib import *

FakeResponses = {'/usr/sbin/smartctl -x /dev/sda': 'testdata/soft_1/smart/1.txt',
                 '/usr/sbin/smartctl -x /dev/sdb': 'testdata/soft_1/smart/2.txt',
                 '/usr/sbin/smartctl -x /dev/sdc': 'testdata/soft_1/smart/3.txt',
                 '/usr/sbin/smartctl -x /dev/sdd': 'testdata/soft_1/smart/4.txt',
                 '/usr/sbin/smartctl -l scterc /dev/sda': 'testdata/soft_1/smart/sct_none.txt',
                 '/usr/sbin/smartctl -l scterc /dev/sdb': 'testdata/soft_1/smart/sct.txt',
                 '/usr/sbin/smartctl -l scterc /dev/sdc': 'testdata/soft_1/smart/sct.txt',
                 '/usr/sbin/smartctl -l scterc /dev/sdd': 'testdata/soft_1/smart/sct.txt'
                 }


def fake_readFile(filename):
    file = open('testdata/soft_1{}'.format(filename))
    lines = [line.strip() for line in file]
    if len(lines) == 1:
        return lines[0]
    return lines

__original_listdir = os.listdir
__original_pathisdir = os.path.isdir


def fake_listdir(dir):
    return __original_listdir('testdata/soft_1{}'.format(dir))


def fake_isdir(dir):
    return __original_pathisdir('testdata/soft_1{}'.format(dir))


def read_file(filename):
    file = open(filename)
    return [line.strip() for line in file]


def fake_isfile(filename):
    if filename in ['/proc/mdstat', '/usr/sbin/smartctl']:
        return True
    return False


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
@mock.patch('os.path.isdir', fake_isdir)
@mock.patch('lib.helpers.getOutput', fake_getOutput)
@mock.patch('lib.helpers.readFile', fake_readFile)
def test_soft_1(monkeypatch):
    controllers = raid.RaidController.probe()
    for controller in controllers:
        controller.printInfo()
