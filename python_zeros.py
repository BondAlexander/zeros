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
import json
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
    global credentials
    credentials = {}
    with open('auth.json', 'r') as fd:
        credentials = json.loads(fd)
    querryimc.main()
    with open('/home/gregorya/zeros/completed_devices_file') as f:

        devices_list = f.read().splitlines()

    start = datetime.datetime.now().strftime("%Y%m%d-%H:%M:%S")

    print('Begin operation - ' + start)


    file_name = datetime.datetime.now().strftime("%Y%m%d-%H%M")

    to_doc_w(file_name, "")



    for devices in devices_list:
        print('Connecting to device ' + devices)
        ip_address_of_device = devices
        hp_devices = {
            'device_type': 'hp_procurve',
            'ip': ip_address_of_device, 
            'username': credentials['SSH']['username'],
            'password': credentials['SSH']['username'],
            'global_delay_factor': .25
        }

        try:
            net_connect = ConnectHandler(**hp_devices)
        except (AuthenticationException):
            print ('********************Authentication failure: ' + ip_address_of_device)
            continue
        except (NetMikoTimeoutException):
            print ('-------------------Timeout to device: ' + ip_address_of_device)
            continue
        except (EOFError):
            print ("End of file while attempting device " + ip_address_of_device)
            continue
        except (SSHException):
            print ('SSH Issue. Are you sure SSH is enabled? ' + ip_address_of_device)
            continue
        except Exception as unknown_error:
            print ('Some other error: ' + str(unknown_error))
            continue


        sysoutput = net_connect.send_command_expect('show system', expect_string=r">")
        intoutput = net_connect.send_command_expect('show interface', expect_string=r">")
        linebreak = "*-*-*-*-" * 15
        finish = datetime.datetime.now().strftime("%Y%m%d-%H:%M:%S")
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