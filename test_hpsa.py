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
                }


def read_file(filename):
    file = open(filename)
    return [line.strip() for line in file]


def fake_isfile(filename):
    if filename == '/opt/compaq/hpacucli/bld/hpacucli':
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
def test_hpsa_1(monkeypatch):
    controllers = raid.RaidController.probe()
    for controller in controllers:
        controller.printInfo()
