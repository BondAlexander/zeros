import pickle
import os
import re
from pprint import pprint


class Database:
    def __init__(self) -> None:
        self.switch_list = []

    def save(self, file_path="database.pickle"):
        with open(file_path, "w") as fd:
            pickle.dump(self, fd)

    def load(self, file_path="database.pickle"):
        if os.path.exists(file_path):
            with open(file_path, "r") as fd:
                self = pickle.load(fd)
        else:
            with open('completed_devices_file', 'r') as fd:
                switch_ips = [ip for ip in fd.read().split('\n') if ip != '']
            self.switch_list = [Switch(switch) for switch in switch_ips]


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
                self.add_port(columns)
        data_start = False
        pprint(self.port_list)

    def add_port(self, port_info):
        port_number = port_info[0]
        port_activity = port_info[1]
        if self.port_list.get(port_number):
            self.port_list[port_number].append(port_activity)
        else:
            self.port_list[port_number] = [port_activity]

