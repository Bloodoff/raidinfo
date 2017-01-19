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
        output = os.popen(cmd)
        for line in output:
            if not re.match(r'^$', line.strip()):
                lines.append(line.strip())
        Outputs[cmd] = lines
    return lines
