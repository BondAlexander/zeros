#!/usr/bin/env python3

import datetime
import logging
import json
import concurrent.futures
import os
import argparse
from src.datastructures import Database
import src.querryimc as querryimc
from src.emailhandler import EmailHandler
from src.switchquerrier import SwitchQuerrier

'''
This function is just to make sure that the logs/ and output/ directories are set up in the project directory. If they 
do not exist, this function creates them
'''
def verify_file_structure():
    if not os.path.exists('logs/'):
        os.mkdir('logs/')
    if not os.path.exists('output/'):
        os.mkdir('output/')


'''
This function sets up the basic logging information such as the file that logs are committed to and the logging level
'''
def setup_logging(file_name):
    logging.basicConfig(filename=file_name)
    logging.getLogger('paramiko.transport').setLevel(logging.CRITICAL)


'''
This function creates arguments for the project along with their help info. The funtion then parses the arguments and handles what needs 
to be done at the program's start accordingly
'''
def handle_arguments(credentials, email_handler):
    parser = argparse.ArgumentParser(description='Arguments for Zeros Program')
    parser.add_argument("-l", "--load-folder", help="Load database from folder of raw output files")
    parser.add_argument("-d", "--project-directory", help="Specify path to project directory (useful for crontab)")
    parser.add_argument("-u", "--update-from-IMC", action='store_true', help="Automatically update completed_devices_file from IMC")
    args = parser.parse_args()
    if args.load_folder:
        print(f'\nLoading from \'{args.load_folder}\' and creating local database \'database.pickle\'...')
        db = Database()
        db.load_from_folder(args.load_folder)
        db.save()
        print('Done.')
        exit(0)
    if args.project_directory:
        os.chdir(args.project_directory)
    if args.update_from_IMC:
        new_switch_list = querryimc.querry_imc(credentials)
        num_changes = SwitchQuerrier.update_list(new_switch_list)
        email_handler.update_email_body(num_ip_changes=num_changes)
    return args


'''
This is the main function to run the project. It starts by loading the config file, creating the EmailHandler object and handling 
arguments for the project. The function then verifies the file structure, sets up the logging information and instantiates then loads 
the database. The function then starts the main functionality of the program by opening the completed_devices_file, and sets up many 
threads of SwitchQuerrier.querry_switch() to ssh into all switches and run a show command and parse that data to be put into the database.
Once all switches are querried, the program saves the database and sends the update email
'''
def main():
    with open('config.json', 'r') as fd:
        credentials = json.loads(fd.read())
    email_handler = EmailHandler()
    handle_arguments(credentials, email_handler)
    print('Begin operation - ')
    verify_file_structure()
    file_name = datetime.datetime.now().strftime("%Y%m%d-%H%M")
    setup_logging(f'logs/{file_name}.log')
    data_base = Database()
    data_base.load()    
    with open('completed_devices_file') as f:
        devices_list = f.read().splitlines()
    num_failed = 0
    sq = SwitchQuerrier(credentials, file_name, data_base)
    with concurrent.futures.ThreadPoolExecutor(max_workers=16) as executor:
        results = executor.map(sq.querry_switch, devices_list)
        for failed, switch in results:
            data_base.update_switch_info(switch)
            num_failed += failed
    print('Operation Complete - ')
    data_base.save()
    data_base.generate_innactivity_report()
    email_handler.update_email_body(num_failed=num_failed, num_devices=len(devices_list))
    email_handler.send_update_email(file_name)

if __name__ == '__main__':
    main()