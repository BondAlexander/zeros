import pickle
import os
import re
from pprint import pprint
from concurrent.futures import ThreadPoolExecutor
from itertools import repeat



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
    def load_from_folder_helper(self, report):
                switch = Switch("PLACEHOLDER")
                lines = [l for l in report.split('\n')]
                for line in lines:
                    columns = [i.replace(',', '') for i in line.split(' ') if i != '']
                    if len(columns) == 0:
                        continue
                    elif re.fullmatch(r'(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9][0-9]|[1-9])\.(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9][0-9]|[0-9])\.(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9][0-9]|[0-9])\.(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9][0-9]|[0-9])', columns[0]):
                        switch = Switch(columns[0])
                switch.read_output(report)

                return switch

    def load_from_folder(self, path):
        for file in os.listdir(path):
            with open(f'{path}/{file}', 'r') as fd:
                switch_reports = [report for report in fd.read().split('*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-')]
                with ThreadPoolExecutor(max_workers=16) as executor:
                    output = executor.map(self.load_from_folder_helper, switch_reports)
                    for switch in output:
                        self.update_switch_info(switch)

    def get_switch_by_ip(self, ip: str):
        for switch in self.switch_list:
            if switch.switch_ip == ip:
                return switch
    
    def update_switch_info(self, switch_to_merge):
        switch_to_update = self.get_switch_by_ip(switch_to_merge.switch_ip)

        if switch_to_update:
            for port in switch_to_merge.port_list.keys():
                if not switch_to_update.port_list.get(port):
                    switch_to_update.port_list[port] = []
                switch_to_update.port_list[port].append(switch_to_merge.port_list[port][0])
        else:
            self.switch_list.append(switch_to_merge)

    def report_innactivity(self):
        report = ""
        for switch in self.switch_list:
            for port_num, port_traffic in switch.port_list.items():
                days_innactive = 0
                for index, traffic in enumerate(reversed(port_traffic)):
                    if index == 0:
                        continue
                    elif traffic == port_traffic[-index]:
                        days_innactive += 1
                    elif traffic > port_traffic[-index-1]:
                        break
                if days_innactive >= 90:
                    report += (f'{switch.switch_ip}:{port_num} inactive {days_innactive} days\n')
            report += '\n'
        with open('report.txt', 'w') as fd:
            fd.write(report)
                


class Switch:
    def __init__(self, ip: str):
        self.switch_ip = ip
        self.port_list = {}

    def read_output(self, text):
        data_start = False
        for line in text.split('\n'):
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
