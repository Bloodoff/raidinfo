#!/usr/bin/python3
import socket
import smtplib
import datetime
import sys
import os
import argparse
from email.mime.text import MIMEText
from io import StringIO
from lib import *


fromaddr = ''
toaddr = ''
mailserver = ''
mailserverport = 519
maillogin = ''
mailpassword = ''


def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--help', help='show this help message and exit', action='store_true')
    parser.add_argument('-e', '--email', help='send report via email', action='store_true')
    args = parser.parse_args()

    if args.help:
        print('Makes a compact report about RAID controllers')
        parser.print_help()
        return 0

    if not os.name == 'nt':
        if os.getenv('USER') != 'root':
            print('This script requires Administrator privileges')
            sys.exit(5)

    if args.email:
        old_stdout = sys.stdout
        sys.stdout = body = StringIO()

    controllers = raid.RaidController.probe()
    for controller in controllers:
        controller.printInfo()

    if args.email:
        sys.stdout = old_stdout
        msg = MIMEText(body.getvalue())
        msg['From'] = fromaddr
        msg['To'] = toaddr
        msg['Subject'] = 'Information about RAID controllers on {}'.format(socket.getfqdn())
        msg['Date'] = datetime.datetime.now().ctime()

        server = smtplib.SMTP(mailserver, mailserverport)
        server.starttls()
        server.login(maillogin, mailpassword)
        text = msg.as_string()
        server.sendmail(fromaddr, toaddr, text)
        server.quit()

if __name__ == '__main__':
    main()
