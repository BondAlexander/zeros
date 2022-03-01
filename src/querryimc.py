#!/usr/bin/env python

from pyhpeimc.auth import IMCAuth
from pyhpeimc.plat.device import get_all_devs
import getpass
import time


'''
This code is based off of the CST_IMC project at Colorado State University's Cybersecurity Internship.
This code was forked 2/28/2022
'''


def authenticate_user(tries=2):
    uname = input("Username: ")
    passwd= getpass.getpass("Password: ")
    ip = "10.100.201.199"
    port = "8080"
    auth = IMCAuth("http://", str(ip), str(port), uname, passwd)

    if '200' not in str(auth.get_auth()):
        if tries == 0:
            print('Too many attemps. Exiting program.')
            exit()
        print(f'You have {tries} more attempts.')
        time.sleep(2)
        authenticate_user(tries-1)
    print("\t*Connected To IMC Server*")
    return auth


def formatDict(dict, key):
    switch_list = ''
    for item in dict:
        if item.get('devCategoryImgSrc') == 'switch':
            switch_list += item['ip'] + '\n'
    return switch_list


def main():
    authentication_token = authenticate_user()

    switch_ips_as_string = formatDict((get_all_devs(authentication_token, "http://10.100.201.199:8080")), 'id')

    with open('completed_devices_file', 'w') as fd:
        fd.write(switch_ips_as_string)


#_____Main_________
if __name__ == '__main__':
    main()