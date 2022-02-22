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
                        'smtp_server' : 'smtp.gmail.com',
                        'watchlist' : ''}
    with open(args.settings_file, 'w') as configfile:
        config.write(configfile)
    print(f"No config file was detected and a new one was generated for you and can be found here: '{args.settings_file}'. Please fill out all fields before continuing.\nQuitting!")
    exit()

try:
    password = str(getpass.getpass('Enter the sending email password: '))
    print('OK!')
    context = ssl.create_default_context()
    downlist = []
    setup_test = False

    while True:
        config.read(args.settings_file)
        config.sections()
        sleeptime   = config['DEFAULT']['interval']
        watchlist   = config['DEFAULT']['watchlist']
        email       = config['DEFAULT']['sender_email']
        reciever    = config['DEFAULT']['recipient_email']
        port        = config['DEFAULT']['smtp_port']
        smtp_server = config['DEFAULT']['smtp_server']
        watchlist   = watchlist.replace(' ', '').split(',')

        if setup_test == False:
            try:
                message = f"Subject: Monitoring Working Correctly. \
                            \nIf you get this message, everything is working correctly. This is just a test. \
                            \nTimestamp: {datetime.datetime.now()}"
                with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
                    server.login(email, password)
                    server.sendmail(email, reciever, message)
                setup_test = True
                print('A test email should have been sent to you. Please check your inbox.')
            except smtplib.SMTPAuthenticationError:
                print('Authentication error! Please check your email authentication details!')
                print('Quitting!')
                exit()
            except:
                print('There is an error in your current email config.')
                print('Quitting!')
                exit()

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
                with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
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