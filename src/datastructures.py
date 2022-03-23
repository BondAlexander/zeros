import pickle
import os
import re
from pprint import pprint


class Database:
    def __init__(self) -> None:
        self.switch_list = []
        self.file_path = "database.pickle"

    def save(self):
        with open(self.file_path, "wb") as fd:
            pickle.dump(self.switch_list, fd)

    def load(self):
        if os.path.exists(self.file_path):
            with open(self.file_path, "rb") as fd:
                self.switch_list = pickle.load(fd)
        else:
            with open('completed_devices_file', 'r') as fd:
                switch_ips = [ip for ip in fd.read().split('\n') if ip != '']
            self.switch_list = [Switch(switch) for switch in switch_ips]

    def get_switch_by_ip(self, ip: str):
        for switch in self.switch_list:
            if switch.switch_ip == ip:
                return switch
    
    def update_switch_info(self, switch_to_merge):

        switch_to_update = self.get_switch_by_ip(switch_to_merge.switch_ip)

        if switch_to_update:
            for port in switch_to_merge.port_list.keys():
                switch_to_update.port_list[port].append(switch_to_merge.port_list[port])
        else:
            self.switch_list.append(switch_to_merge)

class Switch:
    def __init__(self, ip: str):
        self.switch_ip = ip
        self.port_list = {}

    def read_output(self, text):
        data_start = False
        for index, line in enumerate(text.split('\n')):
            columns = [i.replace(',', '') for i in line.split(' ') if i != '']
            if re.fullmatch(r'^-+$',''.join(columns)):
                data_start = True
                continue
            if data_start and len(columns) > 2:
                self.add_data_to_port(columns)

    def add_data_to_port(self, port_info):
        port_number = port_info[0]
        port_activity = port_info[1]
        if self.port_list.get(port_number):
            self.port_list[port_number].append(port_activity)
        else:
            self.port_list[port_number] = [port_activity]
