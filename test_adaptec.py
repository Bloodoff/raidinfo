#!/usr/bin/python3
import os
import re
import pytest
import mock

from lib import *

FakeResponses = {
    '/usr/sbin/arcconf LIST': 'testdata/adaptec/util-1.txt',
    '/usr/sbin/arcconf GETCONFIG 1': 'testdata/adaptec/util-2.txt',
    '/usr/sbin/smartctl -x -d aacraid,0,0,0 /dev/null': 'testdata/adaptec/smart-0.txt',
    '/usr/sbin/smartctl -x -d aacraid,0,0,1 /dev/null': 'testdata/adaptec/smart-1.txt',
    '/usr/sbin/smartctl -x -d aacraid,0,0,2 /dev/null': 'testdata/adaptec/smart-2.txt',
    '/usr/sbin/smartctl -x -d aacraid,0,0,4 /dev/null': 'testdata/adaptec/smart-4.txt',
    '/usr/sbin/smartctl -x -d aacraid,0,0,5 /dev/null': 'testdata/adaptec/smart-5.txt',
    '/usr/sbin/arcconf GETSMARTSTATS 1': 'testdata/adaptec/util-3.txt',
}


def read_file(filename):
    file = open(filename)
    return [line.strip() for line in file]


def fake_isfile(filename):
    if filename in ['/usr/sbin/arcconf', '/usr/sbin/smartctl']:
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


@mock.patch('os.path.isfile', fake_isfile)
@mock.patch('lib.helpers.getOutput', fake_getOutput)
def test_adaptec_1(monkeypatch):
    controllers = raid.RaidController.probe()
    for controller in controllers:
        controller.printInfo()
