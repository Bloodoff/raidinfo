#!/usr/bin/python3
import os
import re
import pytest
import mock

from lib import *

FakeResponses = {
    '/usr/sbin/arcconf LIST': 'testdata/adaptec-2/util-1.txt',
    '/usr/sbin/arcconf GETCONFIG 1': 'testdata/adaptec-2/util-2.txt',
    '/usr/sbin/arcconf GETSMARTSTATS 1': 'testdata/adaptec-2/util-3.txt',
    '/usr/sbin/smartctl -x -d aacraid,0,0,8 /dev/null': 'testdata/adaptec-2/smart-1.txt',
    '/usr/sbin/smartctl -x -d aacraid,0,0,9 /dev/null': 'testdata/adaptec-2/smart-2.txt',
    '/usr/sbin/smartctl -x -d aacraid,0,0,10 /dev/null': 'testdata/adaptec-2/smart-3.txt',
    '/usr/sbin/smartctl -x -d aacraid,0,0,11 /dev/null': 'testdata/adaptec-2/smart-4.txt',
    '/usr/sbin/smartctl -x -d aacraid,0,0,12 /dev/null': 'testdata/adaptec-2/smart-5.txt',
    '/usr/sbin/smartctl -x -d aacraid,0,0,13 /dev/null': 'testdata/adaptec-2/smart-6.txt',
    '/usr/sbin/smartctl -x -d aacraid,0,0,14 /dev/null': 'testdata/adaptec-2/smart-7.txt',
    '/usr/sbin/smartctl -x -d aacraid,0,0,15 /dev/null': 'testdata/adaptec-2/smart-8.txt',
    '/usr/sbin/smartctl -x -d aacraid,0,0,16 /dev/null': 'testdata/adaptec-2/smart-9.txt',
    '/usr/sbin/smartctl -x -d aacraid,0,0,17 /dev/null': 'testdata/adaptec-2/smart-10.txt',
    '/usr/sbin/smartctl -x -d aacraid,0,0,18 /dev/null': 'testdata/adaptec-2/smart-11.txt',
    '/usr/sbin/smartctl -x -d aacraid,0,0,19 /dev/null': 'testdata/adaptec-2/smart-12.txt',
    '/usr/sbin/smartctl -x -d aacraid,0,0,20 /dev/null': 'testdata/adaptec-2/smart-13.txt',
    '/usr/sbin/smartctl -x -d aacraid,0,0,21 /dev/null': 'testdata/adaptec-2/smart-14.txt',
    '/usr/sbin/smartctl -x -d aacraid,0,0,22 /dev/null': 'testdata/adaptec-2/smart-15.txt',
    '/usr/sbin/smartctl -x -d aacraid,0,0,23 /dev/null': 'testdata/adaptec-2/smart-16.txt',
    '/usr/sbin/smartctl -x -d aacraid,0,-,- /dev/null': 'testdata/adaptec/smart-error.txt',
    '/usr/sbin/smartctl -l scterc -d aacraid,0,-,- /dev/null': 'testdata/adaptec/smart-error.txt',
    '/usr/sbin/smartctl -l scterc -d aacraid,0,0,8 /dev/null': 'testdata/adaptec/smart-sct.txt',
    '/usr/sbin/smartctl -l scterc -d aacraid,0,0,9 /dev/null': 'testdata/adaptec/smart-sct.txt',
    '/usr/sbin/smartctl -l scterc -d aacraid,0,0,10 /dev/null': 'testdata/adaptec/smart-sct.txt',
    '/usr/sbin/smartctl -l scterc -d aacraid,0,0,11 /dev/null': 'testdata/adaptec/smart-sct.txt',
    '/usr/sbin/smartctl -l scterc -d aacraid,0,0,12 /dev/null': 'testdata/adaptec/smart-sct.txt',
    '/usr/sbin/smartctl -l scterc -d aacraid,0,0,13 /dev/null': 'testdata/adaptec/smart-sct.txt',
    '/usr/sbin/smartctl -l scterc -d aacraid,0,0,14 /dev/null': 'testdata/adaptec/smart-sct.txt',
    '/usr/sbin/smartctl -l scterc -d aacraid,0,0,15 /dev/null': 'testdata/adaptec/smart-sct.txt',
    '/usr/sbin/smartctl -l scterc -d aacraid,0,0,16 /dev/null': 'testdata/adaptec/smart-sct.txt',
    '/usr/sbin/smartctl -l scterc -d aacraid,0,0,17 /dev/null': 'testdata/adaptec/smart-sct.txt',
    '/usr/sbin/smartctl -l scterc -d aacraid,0,0,18 /dev/null': 'testdata/adaptec/smart-sct.txt',
    '/usr/sbin/smartctl -l scterc -d aacraid,0,0,19 /dev/null': 'testdata/adaptec/smart-sct.txt',
    '/usr/sbin/smartctl -l scterc -d aacraid,0,0,20 /dev/null': 'testdata/adaptec/smart-sct.txt',
    '/usr/sbin/smartctl -l scterc -d aacraid,0,0,21 /dev/null': 'testdata/adaptec/smart-sct.txt',
    '/usr/sbin/smartctl -l scterc -d aacraid,0,0,22 /dev/null': 'testdata/adaptec/smart-sct.txt',
    '/usr/sbin/smartctl -l scterc -d aacraid,0,0,23 /dev/null': 'testdata/adaptec/smart-sct.txt',
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
def test_adaptec_2(monkeypatch):
    controllers = raid.RaidController.probe()
    for controller in controllers:
        controller.printInfo()
