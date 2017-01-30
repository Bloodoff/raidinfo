#!/usr/bin/python3
import os
import re
import pytest
import time


from lib import *

def test_helpers_1(monkeypatch):
    output1 = helpers.getOutput('dd if=/dev/urandom bs=512 count=1 | sha512sum')
    output2 = helpers.getOutput('dd if=/dev/urandom bs=512 count=1 | sha512sum')
    assert output1 == output2
