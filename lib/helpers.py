import subprocess
import os
import re


def readFile(filename):
    file = open(filename)
    lines = [line.strip() for line in file]
    if len(lines) == 1:
        return lines[0]
    return lines

Outputs = {}


def getOutput(cmd):
    lines = []
    if (cmd in Outputs):
        lines = Outputs[cmd]
    else:
        startupinfo = None
        shell = True
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            shell = False
        output = subprocess.Popen(cmd,
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE,
                                  stdin=subprocess.PIPE,
                                  shell=shell,
                                  startupinfo=startupinfo).communicate()
        output = output[0].decode('utf-8', 'ignore').split('\r\n')
        for line in output:
            if not re.match(r'^$', line.strip()):
                lines.append(line.strip())
        Outputs[cmd] = lines
    return lines
