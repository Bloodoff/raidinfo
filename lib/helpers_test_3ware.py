import os
import re
import sys

FakeResponces = { '/usr/sbin/tw_cli show'           : 'testdata/3ware/1.txt',
                  '/usr/sbin/tw_cli /c6 show'       : 'testdata/3ware/2.txt',
                  '/usr/sbin/tw_cli /c6/u0 show all': 'testdata/3ware/3.txt',
                  '/usr/sbin/tw_cli /c6/p0 show all': 'testdata/3ware/4.txt',
                  '/usr/sbin/tw_cli /c6/p1 show all': 'testdata/3ware/5.txt',
                  '/usr/sbin/tw_cli /c6 show all'   : 'testdata/3ware/6.txt'
                  }

def readFile(filename):
    file  = open(filename)
    lines = [line.strip() for line in file]
    if len(lines) == 1:
        return lines[0]
    return lines

Outputs = {}

def getOutput(cmd):
    lines = []
    if ( Outputs.has_key(cmd) ):
        lines = Outputs[cmd]
    else:
        testfile = FakeResponces.get(cmd, False)
        if not testfile:
            print 'Test file for command "{}" not found'.format(cmd)
            sys.exit(12)
        output = readFile('{}/{}'.format(os.path.dirname(__file__), testfile))
        for line in output:
            if not re.match(r'^$',line.strip()):
                lines.append(line.strip())
        Outputs[cmd] = lines
    return lines
