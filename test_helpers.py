#!/usr/bin/python3
import os
import re
import pytest
import time


from lib import *

def test_helpers_1(monkeypatch):
    output1 = helpers.getOutput('/bin/shuf -i1-100000 -n1')
    output2 = helpers.getOutput('/bin/shuf -i1-100000 -n1')
    assert output1 == output2
