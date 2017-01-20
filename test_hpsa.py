#!/usr/bin/python3
import os
import re
import pytest
import mock

from lib import *

FakeResponses = {'/opt/compaq/hpacucli/bld/hpacucli controller all show'   : 'testdata/hpsa/1.txt',
                 '/opt/compaq/hpacucli/bld/hpacucli controller slot=2 show': 'testdata/hpsa/2.txt',
                 '/opt/compaq/hpacucli/bld/hpacucli controller slot=0 show': 'testdata/hpsa/3.txt',
                 '/opt/compaq/hpacucli/bld/hpacucli controller slot=0 array A logicaldrive all show': 'testdata/hpsa/4.txt',
                 '/opt/compaq/hpacucli/bld/hpacucli controller slot=2 array A logicaldrive all show': 'testdata/hpsa/5.txt',
                 '/opt/compaq/hpacucli/bld/hpacucli controller slot=2 array all show': 'testdata/hpsa/6.txt',
                 '/opt/compaq/hpacucli/bld/hpacucli controller slot=0 array all show': 'testdata/hpsa/7.txt',
                 '/opt/compaq/hpacucli/bld/hpacucli controller slot=2 array A physicaldrive all show': 'testdata/hpsa/8.txt',
                 '/opt/compaq/hpacucli/bld/hpacucli controller slot=0 array A physicaldrive all show': 'testdata/hpsa/9.txt',
                 '/opt/compaq/hpacucli/bld/hpacucli controller slot=2 physicaldrive 2E:1:1 show': 'testdata/hpsa/10.txt',
                 '/opt/compaq/hpacucli/bld/hpacucli controller slot=2 physicaldrive 2E:1:2 show': 'testdata/hpsa/11.txt',
                 '/opt/compaq/hpacucli/bld/hpacucli controller slot=2 physicaldrive 2E:1:3 show': 'testdata/hpsa/12.txt',
                 '/opt/compaq/hpacucli/bld/hpacucli controller slot=2 physicaldrive 2E:1:4 show': 'testdata/hpsa/13.txt',
                 '/opt/compaq/hpacucli/bld/hpacucli controller slot=2 physicaldrive 2E:1:5 show': 'testdata/hpsa/14.txt',
                 '/opt/compaq/hpacucli/bld/hpacucli controller slot=2 physicaldrive 2E:1:6 show': 'testdata/hpsa/15.txt',
                 '/opt/compaq/hpacucli/bld/hpacucli controller slot=2 physicaldrive 2E:1:7 show': 'testdata/hpsa/16.txt',
                 '/opt/compaq/hpacucli/bld/hpacucli controller slot=2 physicaldrive 2E:1:8 show': 'testdata/hpsa/17.txt',
                 '/opt/compaq/hpacucli/bld/hpacucli controller slot=2 physicaldrive 2E:1:9 show': 'testdata/hpsa/18.txt',
                 '/opt/compaq/hpacucli/bld/hpacucli controller slot=2 physicaldrive 2E:1:10 show': 'testdata/hpsa/10.txt',
                 '/opt/compaq/hpacucli/bld/hpacucli controller slot=2 physicaldrive 2E:1:11 show': 'testdata/hpsa/20.txt',
                 '/opt/compaq/hpacucli/bld/hpacucli controller slot=2 physicaldrive 2E:1:12 show': 'testdata/hpsa/21.txt',
                 '/opt/compaq/hpacucli/bld/hpacucli controller slot=0 physicaldrive 1I:1:1 show': 'testdata/hpsa/22.txt',
                 '/opt/compaq/hpacucli/bld/hpacucli controller slot=0 physicaldrive 1I:1:2 show': 'testdata/hpsa/23.txt',
                 '/opt/compaq/hpacucli/bld/hpacucli controller slot=0 physicaldrive 1I:1:3 show': 'testdata/hpsa/24.txt',
                 '/opt/compaq/hpacucli/bld/hpacucli controller slot=0 physicaldrive 1I:1:4 show': 'testdata/hpsa/25.txt',
                 '/opt/compaq/hpacucli/bld/hpacucli controller slot=0 physicaldrive 2I:1:5 show': 'testdata/hpsa/26.txt',
                 '/opt/compaq/hpacucli/bld/hpacucli controller slot=0 physicaldrive 2I:1:6 show': 'testdata/hpsa/27.txt',
                 '/opt/compaq/hpacucli/bld/hpacucli controller slot=0 physicaldrive 2I:1:7 show': 'testdata/hpsa/28.txt',
                 '/opt/compaq/hpacucli/bld/hpacucli controller slot=0 physicaldrive 2I:1:8 show': 'testdata/hpsa/29.txt',
                 '/usr/sbin/smartctl -x -d cciss,0 /dev/sg1': 'testdata/hpsa/smart/1.txt',
                 '/usr/sbin/smartctl -x -d cciss,1 /dev/sg1': 'testdata/hpsa/smart/2.txt',
                 '/usr/sbin/smartctl -x -d cciss,2 /dev/sg1': 'testdata/hpsa/smart/3.txt',
                 '/usr/sbin/smartctl -x -d cciss,3 /dev/sg1': 'testdata/hpsa/smart/4.txt',
                 '/usr/sbin/smartctl -x -d cciss,4 /dev/sg1': 'testdata/hpsa/smart/5.txt',
                 '/usr/sbin/smartctl -x -d cciss,5 /dev/sg1': 'testdata/hpsa/smart/6.txt',
                 '/usr/sbin/smartctl -x -d cciss,6 /dev/sg1': 'testdata/hpsa/smart/7.txt',
                 '/usr/sbin/smartctl -x -d cciss,7 /dev/sg1': 'testdata/hpsa/smart/8.txt',
                 '/usr/sbin/smartctl -x -d cciss,8 /dev/sg1': 'testdata/hpsa/smart/9.txt',
                 '/usr/sbin/smartctl -x -d cciss,0 /dev/sg3': 'testdata/hpsa/smart/10.txt',
                 '/usr/sbin/smartctl -x -d cciss,1 /dev/sg3': 'testdata/hpsa/smart/11.txt',
                 '/usr/sbin/smartctl -x -d cciss,2 /dev/sg3': 'testdata/hpsa/smart/12.txt',
                 '/usr/sbin/smartctl -x -d cciss,3 /dev/sg3': 'testdata/hpsa/smart/13.txt',
                 '/usr/sbin/smartctl -x -d cciss,4 /dev/sg3': 'testdata/hpsa/smart/14.txt',
                 '/usr/sbin/smartctl -x -d cciss,5 /dev/sg3': 'testdata/hpsa/smart/15.txt',
                 '/usr/sbin/smartctl -x -d cciss,6 /dev/sg3': 'testdata/hpsa/smart/16.txt',
                 '/usr/sbin/smartctl -x -d cciss,7 /dev/sg3': 'testdata/hpsa/smart/17.txt',
                 '/usr/sbin/smartctl -x -d cciss,8 /dev/sg3': 'testdata/hpsa/smart/18.txt',
                 '/usr/sbin/smartctl -x -d cciss,9 /dev/sg3': 'testdata/hpsa/smart/19.txt',
                 '/usr/sbin/smartctl -x -d cciss,10 /dev/sg3': 'testdata/hpsa/smart/20.txt',
                 '/usr/sbin/smartctl -x -d cciss,11 /dev/sg3': 'testdata/hpsa/smart/21.txt',
                 '/usr/sbin/smartctl -x -d cciss,12 /dev/sg3': 'testdata/hpsa/smart/22.txt',
}


def read_file(filename):
    file = open(filename)
    return [line.strip() for line in file]


def fake_isfile(filename):
    if filename == '/opt/compaq/hpacucli/bld/hpacucli':
        return True
    return False


def fake_readFile(filename):
    file = open('testdata/hpsa{}'.format(filename))
    lines = [line.strip() for line in file]
    if len(lines) == 1:
        return lines[0]
    return lines


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
@mock.patch('lib.helpers.readFile', fake_readFile)
def test_hpsa_1(monkeypatch):
    controllers = raid.RaidController.probe()
    for controller in controllers:
        controller.printInfo()
