#!/usr/bin/env python

from pyhpeimc.auth import IMCAuth
from pyhpeimc.plat.device import get_all_devs

'''
This code is based off of the CST_IMC project at Colorado State University's Cybersecurity Internship.
This code was forked 2/28/2022
'''


def authenticate_user(credentials, tries=2):
    uname = credentials['IMC']['username']
    passwd= credentials['IMC']['password']
    ip = "10.100.201.199"
    port = "8080"
    auth = IMCAuth("http://", str(ip), str(port), uname, passwd)
    if '200' not in str(auth.get_auth()):
        print('Incorrect credentials for IMC server. Exiting...')
        exit(0)
    print("\t*Connected To IMC Server*")
    return auth


def formatDict(dict, key):
    switch_list = ''
    for item in dict:
        if item.get('devCategoryImgSrc') == 'switch':
            switch_list += item['ip'] + '\n'
    return switch_list


def main(credentials: dict):
    authentication_token = authenticate_user(credentials)
    switch_ips_as_string = formatDict((get_all_devs(authentication_token, "http://10.100.201.199:8080")), 'id')
    with open('completed_devices_file', 'w') as fd:
        fd.write(switch_ips_as_string)


#_____Main_________
if __name__ == '__main__':
    main()