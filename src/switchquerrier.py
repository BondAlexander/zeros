from src.datastructures import Switch
import logging
import datetime
from netmiko import ConnectHandler
from netmiko.ssh_exception import NetMikoTimeoutException
from paramiko.ssh_exception import SSHException
from netmiko.ssh_exception import AuthenticationException


'''
The SwitchQuerrier class instantiates an object that retrieves data from all switches specified in completed_devices_file.
This class also has several static methods for updating the completed_devices_file
'''
class SwitchQuerrier:
    def __init__(self, credentials, file_name, database):
        self.hp_devices = {
            'device_type': 'hp_procurve',
            'ip': "0.0.0.0",
            'username': credentials['SSH']['username'],
            'password': credentials['SSH']['password'],
            'global_delay_factor': .25
        }
        self.file_name = file_name
        self.database = database

    '''
    This is an internal helper method for updating the SwitchQuerrier ip field in self.hp_devices
    '''
    def _update_ip(self, new_ip):
        self.hp_devices['ip'] = new_ip

    '''
    This method is given a switch IP and querries the switch at that IP and calls a method that parses the output of the show command
    while handling common exceptions associated with failed connections and logs them to the .log file. The method then returns the update
    of the total number of switches that have failed along with a new object for the switch that was querried
    '''
    def querry_switch(self, switch_ip):
        self._update_ip(switch_ip)
        new_switch = Switch(switch_ip)
        num_failed = 0
        for attempt in [1, 2]:
            try:
                if attempt == 1:
                    net_connect = ConnectHandler(timeout=3, **self.hp_devices)
                else:
                    net_connect = ConnectHandler(timeout=10, **self.hp_devices)
            except (AuthenticationException):
                logging.error('Authentication failure: ' + switch_ip)
                num_failed += 1
                break
            except (NetMikoTimeoutException):
                if attempt == 1:
                    print(f'-------------------Timeout to device: {switch_ip}\nRetrying...')
                    continue
                else:
                    logging.error(f'Timeout to device: {switch_ip} Skipping...')
                    num_failed += 1
                    break
            except (EOFError):
                logging.error("End of file while attempting device " + switch_ip)
                num_failed += 1
                break
            except (SSHException):
                logging.error('SSH Issue. Are you sure SSH is enabled? ' + switch_ip)
                num_failed += 1
                break
            except Exception as unknown_error:
                logging.error('Some other error: ' + str(unknown_error))
                num_failed += 1
                break
            try:
                sysoutput = net_connect.send_command_expect('show system', expect_string=r"")
                intoutput = net_connect.send_command_expect('show interface', expect_string=r"")
            except OSError as e:
                logging.error(f'Unexpected output format received from {switch_ip}: \"{e}\"')
                continue
            linebreak = "*-*-*-*-" * 15
            finish = datetime.datetime.now().strftime("%Y%m%d-%H:%M:%S")
            net_connect.disconnect()
            print('Operation Complete - ' + finish)
            print('\n')
            new_switch.read_output(intoutput, self.database)
            self.raw_output_writer(f'output/{self.file_name}', switch_ip, sysoutput, intoutput, linebreak, finish)
            break
        return num_failed, new_switch

    '''
    This method updates the list of switch IPs stored in the completed_devices_file and calls on a method to log the changes made
    '''
    @staticmethod
    def update_list(new_switch_list):
        num_changes = 0
        new_switch_ips = SwitchQuerrier.parse_switch_list(new_switch_list)
        with open('completed_devices_file', 'r') as fd:
            old_switch_ips = fd.read().split('\n')
        SwitchQuerrier.log_switch_updates(old_switch_ips, new_switch_ips)
        with open('completed_devices_file', 'w') as fd:
            fd.write('\n'.join(new_switch_ips))
        return num_changes

    '''
    This method is meant to receive the switch list returned by IMC and return only the IPs of devices identified as network switches
    '''
    @staticmethod
    def parse_switch_list(dict):
        switch_list = []
        for item in dict:
            if item.get('devCategoryImgSrc') == 'switch':
                switch_list.append(item['ip'])
        return switch_list

    '''
    This method is for logging any changes made between the old_switch_ips list and the new_switch_ips list
    '''
    @staticmethod
    def log_switch_updates(old_switch_ips, new_switch_ips):
        for ip in old_switch_ips:
            if ip not in new_switch_ips:
                logging.warning(f'Removing {ip} from list of switches')
                num_changes += 1
        for ip in new_switch_ips:
            if ip not in old_switch_ips:
                logging.warning(f'Adding {ip} to list of switches')
                num_changes += 1

    '''
    This method is for writing all data to the raw switch output file specified for file_name. The second parameter takes a variable
    number of arguments that the method loops through, appending all of the variables into the file specified with the first parameter
    '''
    @staticmethod
    def raw_output_writer(file_name, *args):
        with open(file_name, 'a') as f:
            for v in args:
                f.write(v)
                f.write('\n')    