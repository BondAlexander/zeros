#!/usr/bin/env python3


#v1 Initial base code that handles errors through netmiko.
#v2 Writing output to a file.
#v3 integrating username and pw into code
#v4 Adding start and end times and linebreak
#v5 Sending output to a file
#v6 --TODO - Write errors received to file along with screen, add blank lines to file after each switch.
#v7 Minor tweaks
#v8 Working with Global Delay Factor and search patterns



#from getpass import getpass
import datetime
from fileinput import filename
import logging
import json
import sys
import os
import src.querryimc as querryimc
from netmiko import ConnectHandler
from netmiko.ssh_exception import NetMikoTimeoutException
from paramiko.ssh_exception import SSHException
from netmiko.ssh_exception import AuthenticationException




def to_doc_a(file_name, varable):
    f=open(file_name, 'a')
    f.write(varable)
    f.write('\n')
    f.close()


def to_doc_w(file_name, varable):
    f=open(file_name, 'w')
    f.write(varable)
    f.close()

def main():
    file_name = datetime.datetime.now().strftime("%Y%m%d-%H%M")
    if not os.path.exists('logs/'):
        os.mkdir('logs/')
    fname = f'logs/{filename}.log'
    logging.basicConfig(filename=fname)
    credentials = {}
    with open('auth.json', 'r') as fd:
        credentials = json.loads(fd.read())
    querryimc.main(credentials)
    with open('/home/gregorya/zeros/completed_devices_file') as f:

        devices_list = f.read().splitlines()

    start = datetime.datetime.now().strftime("%Y%m%d-%H:%M:%S")

    print('Begin operation - ' + start)

    to_doc_w(file_name, "")



    for devices in devices_list:
        for attempt in [1,2]:
            print('Connecting to device ' + devices)
            ip_address_of_device = devices
            hp_devices = {
                'device_type': 'hp_procurve',
                'ip': ip_address_of_device, 
                'username': credentials['SSH']['username'],
                'password': credentials['SSH']['password'],
                'global_delay_factor': .25
            }

            try:
                if attempt == 2:
                    net_connect = ConnectHandler(timeout=3, **hp_devices)
                else:
                    net_connect = ConnectHandler(timeout=10, **hp_devices)
            except (AuthenticationException):
                print ('********************Authentication failure: ' + ip_address_of_device)
                break
            except (NetMikoTimeoutException):
                if attempt == 1:
                    print(f'-------------------Timeout to device: {ip_address_of_device}\nRetrying...')
                    continue
                else:
                    logging.warning(f'-------------------Timeout to device: {ip_address_of_device}\nSkipping...')
                    break
            except (EOFError):
                logging.warning("End of file while attempting device " + ip_address_of_device)
                break
            except (SSHException):
                logging.warning('SSH Issue. Are you sure SSH is enabled? ' + ip_address_of_device)
                break
            except Exception as unknown_error:
                logging.warning('Some other error: ' + str(unknown_error))
                break

            try:
                sysoutput = net_connect.send_command_expect('show system', expect_string=r">")
                intoutput = net_connect.send_command_expect('show interface', expect_string=r">")
            except OSError as e:
                print(e)
                continue
            linebreak = "*-*-*-*-" * 15
            finish = datetime.datetime.now().strftime("%Y%m%d-%H:%M:%S")
            net_connect.disconnect()
            print('Operation Complete - ' + finish)
            print('\n' * 1)
            #Append the output to the results file
            to_doc_a(file_name, devices)
            to_doc_a(file_name, sysoutput)
            to_doc_a(file_name, intoutput)
            to_doc_a(file_name, linebreak)
            to_doc_a(file_name, finish)


    finish = datetime.datetime.now().strftime("%Y%m%d-%H:%M:%S")
    
    print('Operation Complete - ' + finish)

if __name__ == '__main__':
    main()