#!/usr/bin/python3

import os
import time
import configparser
import argparse
import smtplib, ssl
import getpass
import datetime

parser = argparse.ArgumentParser()
parser.add_argument('-s', '--settings', dest='settings_file', default='settings.ini', help='Define which settings file to read from')
args = parser.parse_args()

config = configparser.ConfigParser()

if not os.path.exists(args.settings_file):
    config['DEFAULT'] = {'interval' : '10',
                        'sender_email' : '',
                        'recipient_email' : '',
                        'smtp_port' : '465',
                        'watchlist' : ''}
    with open(args.settings_file, 'w') as configfile:
        config.write(configfile)
    print(f"No config file was detected and a new one was generated for you and can be found here: '{args.settings_file}'. Please fill out all fields before continuing.\nQuitting!")
    exit()

try:
    password = str(getpass.getpass('Enter the sending email password: '))
    context = ssl.create_default_context()
    downlist = []

    while True:
        config.read(args.settings_file)
        config.sections()
        sleeptime   = config['DEFAULT']['interval']
        watchlist   = config['DEFAULT']['watchlist']
        email       = config['DEFAULT']['sender_email']
        reciever    = config['DEFAULT']['recipient_email']
        port        = config['DEFAULT']['smtp_port']
        watchlist   = watchlist.replace(' ', '').split(',')
        for ip in watchlist:
            response = os.system(f"ping -c 1 {ip} >> /dev/null 2>&1")
            if response == 0:
                if ip in downlist:
                    downlist.remove(ip)
            elif ip in downlist:
                continue
            else:
                message = f"Subject: Warning! Server Down! \
                            \n{ip} is down! \nIf this is expexted please ignore this message. \
                            \nTimestamp: {datetime.datetime.now()}"
                with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
                    server.login(email, password)
                    server.sendmail(email, reciever, message)
                downlist.append(ip)
        time.sleep(int(sleeptime) * 60)
except KeyboardInterrupt:
    print('\nQuitting!')
    exit()
except TypeError:
    print(f'\nIncomplete settings file. Check "{args.settings_file}" and fill out the missing/wrong info')
    exit()