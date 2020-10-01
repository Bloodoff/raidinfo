import subprocess
import os
import re

try:
    from functools import lru_cache
except ImportError:
    from polyfills import lru_cache


def readFile(filename):
    if os.path.isfile(filename):
        file = open(filename)
        lines = [line.strip() for line in file]
        if len(lines) == 1:
            return lines[0]
        return lines
    return None


if os.name == 'nt':
    line_separator = '\r\n'
else:
    line_separator = '\n'
 

@lru_cache(maxsize=None)
def getOutput(cmd):
    lines = []
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
    output = output[0].decode('utf-8', 'ignore').split(line_separator)
    for line in output:
        if not re.match(r'^$', line.strip()):
            lines.append(line.strip())
    return lines
