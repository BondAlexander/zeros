from src.datastructures import Switch
import logging
import datetime
from netmiko import ConnectHandler
from netmiko.ssh_exception import NetMikoTimeoutException
from paramiko.ssh_exception import SSHException
from netmiko.ssh_exception import AuthenticationException


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

    def _update_ip(self, new_ip):
        self.hp_devices['ip'] = new_ip

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

    @staticmethod
    def parse_switch_list(dict):
        switch_list = []
        for item in dict:
            if item.get('devCategoryImgSrc') == 'switch':
                switch_list.append(item['ip'])
        return switch_list

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

    @staticmethod
    def raw_output_writer(file_name, *args):
        with open(file_name, 'a') as f:
            for v in args:
                f.write(v)
                f.write('\n')    