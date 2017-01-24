#!/usr/bin/python3
import os
import re
import pytest
import time


from lib import *

def test_helpers_1(monkeypatch):
    output1 = helpers.getOutput('date')
    time.sleep(2) 
    output2 = helpers.getOutput('date')
    assert output1 == output2
    
