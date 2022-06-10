import pickle
import os
import re
from pprint import pprint
from concurrent.futures import ThreadPoolExecutor
from itertools import repeat
import time
import datetime


'''
The Database class is used to handle the loading, saving and updating of the Python database. By default the database will be 
stored as a file called database.pickle which can be loaded in by custom Python code and parsed with Python 
'''
class Database:
    def __init__(self) -> None:
        self.switch_list = []
        self.file_path = "database.pickle"
        self.days_recorded = 0

    '''
    This method handles the saving of the Database instance using the Pickle library
    '''
    def save(self):
        with open(self.file_path, "wb") as fd:
            pickle.dump(self, fd)

    '''
    This method is for loading the pickled database file and updating the Database object's attributes to the saved copy
    '''
    def load(self):
        if os.path.exists(self.file_path):
            with open(self.file_path, "rb") as fd:
                temp_db = pickle.load(fd)
                self.switch_list, self.days_recorded = temp_db.switch_list, temp_db.days_recorded
        else:
            with open('completed_devices_file', 'r') as fd:
                switch_ips = [ip for ip in fd.read().split('\n') if ip != '']
            self.switch_list = [Switch(switch) for switch in switch_ips]

    '''
    This is a helper method for load_from_folder which parses through a raw output file, looping through each line and splitting up
    the columns into a list using a list comprehension. If the regex finds an IP, the method instantiates a Switch object with the columns
    variable and calls the Switch.read_output() method to populate the Switch object's attributes and returns the Switch object
    '''
    def _load_from_folder_helper(self, report, file_name):
        switch = Switch("PLACEHOLDER")
        lines = [l for l in report.split('\n')]
        for line in lines:
            columns = [i.replace(',', '') for i in line.split(' ') if i != '']
            if len(columns) == 0:
                continue
            elif re.fullmatch(r'(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9][0-9]|[1-9])\.(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9][0-9]|[0-9])\.(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9][0-9]|[0-9])\.(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9][0-9]|[0-9])', columns[0]):
                switch = Switch(columns[0])
        entree_date = int(datetime.datetime(int(file_name[:4]), int(file_name[4:6]), int(file_name[6:8])).strftime('%s')) // 86400
        switch.read_output(report, self, entree_date)
        return switch

    '''
    This method loops through all files in a specified directory creates a thread pool for creating objects for all switches listed in the
    raw output files. The self.days_recorded fields is used in other methods to delete data after 120 days
    '''
    def load_from_folder(self, path):
        for file in sorted(os.listdir(path)):
            if self.days_recorded != 120:
                self.days_recorded += 1
            with open(f'{path}/{file}', 'r') as fd:
                switch_reports = [report for report in fd.read().split('*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-')]
                with ThreadPoolExecutor(max_workers=16) as executor:
                    output = executor.map(self._load_from_folder_helper, switch_reports, repeat(file))
                    for switch in output:
                        self.update_switch_info(switch)

    '''
    This is a get method which takes an IP address and returns a Switch object matching that IP if it is found in the database
    '''
    def get_switch_by_ip(self, ip: str):
        for switch in self.switch_list:
            if switch.switch_ip == ip:
                return switch
    
    '''
    This method takes a Switch object and checks to see if it is already listed in the database. If the switch does exist, this method
    update's the activity info for the Switch object. If the switch does not exist then the method creates a new Switch object and appends
    it to the Database
    '''
    def update_switch_info(self, switch_to_merge):
        switch_to_update = self.get_switch_by_ip(switch_to_merge.switch_ip)
        if switch_to_update:
            for port in switch_to_merge.port_list.keys():
                if not switch_to_update.port_list.get(port):
                    switch_to_update.port_list[port] = []
                switch_to_update.port_list[port].append(switch_to_merge.port_list[port][0])
                if len(switch_to_update.port_list.get(port)) > 120:
                    switch_to_update.port_list.get(port).pop(0) 
        else:
            self.switch_list.append(switch_to_merge)

    '''
    This method parses through all Switch objects in the database and checks how many days the Switch has been innactive. This generates a report file
    that lists the days innactive of each port
    '''
    def generate_innactivity_report(self):
        report = ""
        for switch in self.switch_list:
            for port_num, port_traffic in switch.port_list.items():
                days_innactive = 0
                for index, traffic in enumerate(reversed(port_traffic)):
                    if index == 0:
                        continue
                    elif traffic['activity'] == port_traffic[-index]['activity']:
                        days_innactive += 1
                    elif traffic['activity'] > port_traffic[-index-1]['activity']:
                        break
                if days_innactive >= 90:
                    report += (f'{switch.switch_ip}:{port_num} inactive {days_innactive} days\n')
            report += '\n'
        with open('report.txt', 'w') as fd:
            fd.write(report)
                

'''
The Switch class is a datastructure for switches stored in the Database class
'''
class Switch:
    def __init__(self, ip: str):
        self.switch_ip = ip
        self.port_list = {}

    '''
    This method reads the output generated by a show command and updates the port activity data for the switch. The method then
    pads any missing data with 0s.
    '''
    def read_output(self, text, database, epoch_days=time.time() // 86400):
        data_start = False
        for line in text.split('\n'):
            columns = [i.replace(',', '') for i in line.split(' ') if i != '']
            if re.fullmatch(r'^-+$',''.join(columns)):
                data_start = True
                continue
            if data_start and len(columns) > 2:
                self.add_data_to_port(columns, epoch_days=epoch_days)
        self.pad_data(database, epoch_days)

    '''
    This method is used by read_output() to pad any missing port entry that was previously reported with 0s
    '''
    def pad_data(self, database, epoch_days):
        for port in self.port_list.values():
            if len(port) != database.days_recorded:
                for _ in range(database.days_recorded - len(port)):
                    port.append({'activity': '0', 'date': epoch_days})
    
    '''
    This method parses the columns listed in a show command as the parameter 'port_info' and adds the data to the port info in the
    port_list attribute
    '''
    def add_data_to_port(self, port_info, epoch_days):
        port_number = port_info[0]
        port_activity = port_info[1]
        port_entry = {
                "activity": port_activity,
                "date": epoch_days # days since Jan 1st 1970
            }
        if self.port_list.get(port_number):
            self.port_list[port_number].append(port_entry)
        else:
            self.port_list[port_number] = [port_entry]
