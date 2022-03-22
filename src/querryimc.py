#!/usr/bin/env python

import logging
from pyhpeimc.auth import IMCAuth
from pyhpeimc.plat.device import get_all_devs
import os

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


def formatDict(dict):
    switch_list = []
    for item in dict:
        if item.get('devCategoryImgSrc') == 'switch':
            switch_list.append(item['ip'])
    return switch_list


def update_list(new_switch_list):
    new_switch_ips = formatDict(new_switch_list)
    with open('completed_devices_file', 'r') as fd:
        old_switch_ips = fd.read().split('\n')
    for ip in old_switch_ips:
        if ip not in new_switch_ips:
            logging.warning(f'Removing {ip} from list of switches')
    for ip in new_switch_ips:
        if ip not in old_switch_ips:
            logging.warning(f'Adding {ip} to list of switches')
    with open('completed_devices_file', 'w') as fd:
        fd.write('\n'.join(new_switch_ips))


def main(credentials: dict):
    authentication_token = authenticate_user(credentials)
    new_switch_list = get_all_devs(authentication_token, "http://10.100.201.199:8080")
    update_list(new_switch_list)


#_____Main_________
if __name__ == '__main__':
    main()