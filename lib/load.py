import re


def readFile(filename):
    file = open(filename)
    lines = [line.strip() for line in file]
    if len(lines) == 1:
        return lines[0]
    return lines

report = readFile('100.txt')
host_section = False
for line in report:
    match = re.search(r'^Nmap scan report for (.*)$', line)
    if match:
        host_section = True
        host = {}
        host['ip'] = match.group(1)
        host['detail'] = []
        continue
    match = re.search(r'^MAC Address: (\S+)', line)
    if match:
        host_section = False
        host['mac'] = match.group(1)
        print(host)
        continue
    if host_section:
        host['detail'].append(line)
