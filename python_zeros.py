#!/usr/bin/env python3

#v1 Initial base code that handles errors through netmiko.
#v2 Writing output to a file.
#v3 integrating username and pw into code
#v4 Adding start and end times and linebreak
#v5 Sending output to a file
#v6 --TODO - Write errors received to file along with screen, add blank lines to file after each switch.
#v7 Minor tweaks
#v8 Working with Global Delay Factor and search patterns

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


def verify_file_structure():
    if not os.path.exists('logs/'):
        os.mkdir('logs/')
    if not os.path.exists('output/'):
        os.mkdir('output/')


def setup_logging(file_name):
    logging.basicConfig(filename=file_name)
    logging.getLogger('paramiko.transport').setLevel(logging.CRITICAL)


def handle_arguments():
    parser = argparse.ArgumentParser(description='Arguments for Zeros Program')
    parser.add_argument("-l", "--load-folder", help="Load database from folder of raw output files")
    parser.add_argument("-d", "--project-directory", help="Specify path to project directory (useful for crontab)")
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
    return args


def main():
    handle_arguments()
    file_name = datetime.datetime.now().strftime("%Y%m%d-%H%M")
    verify_file_structure()
    setup_logging(f'logs/{file_name}.log')
    data_base = Database()
    data_base.load()
    with open('config.json', 'r') as fd:
        credentials = json.loads(fd.read())
    num_changes = querryimc.querry_imc(credentials)
    with open('completed_devices_file') as f:
        devices_list = f.read().splitlines()
    print('Begin operation - ')
    num_failed = 0
    sq = SwitchQuerrier(credentials, file_name, data_base)
    with concurrent.futures.ThreadPoolExecutor(max_workers=16) as executor:
        results = executor.map(sq.querry_switch, devices_list)
        for failed, switch in results:
            data_base.update_switch_info(switch)
            num_failed += failed
    print('Operation Complete - ')
    email_handler = EmailHandler()
    data_base.save()
    data_base.generate_innactivity_report()
    email_handler.update_email_body(num_changes, num_failed, len(devices_list))
    email_handler.send_update_email(file_name)

if __name__ == '__main__':
    main()