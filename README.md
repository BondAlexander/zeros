# Zeros Project
This project is used by the Colorado State University's networking team in the Division of IT to identify network switch ports that have been innactive for 90+ days. By default, this project will also report that information to a recpient which can be specified in the config

## Installing the project
* You can download this code by running 
```
git clone https://github.com/BondAlexander/zeros.git
```
* Next install all dependencies by running the command below
```
pip3 install -r requirements.txt
```

## Configuring the project
* The `config.json` file will need to be filled out for the project to work

* The 'IMC' section must have credentials that are authorized for the IMC server as well as the IP and port info for the IMC server
* The 'SSH' section must be filled out with user credentials that are authorized for remote access to all the network switches 
* The 'Email' section pertains to the automated emailing. An email username as well as mailserver IP or url will need to be specified along with the port number. The 'recipient' portion should be the email address that is to receive automated emails

## Running the code
* The program will output a file containing the full output from all switches registered on IMC and send the file to the email address specified in `config.json` under Email > recipient
* To run the project you can type the command below
```
python3 python_zeros.py
```
* To view the available arguments use the following command
```
python3 python_zeros.py --help
```
* If you are running the project as an autmated task or cronjob you will need to run the following command
```
python3 python_zeros.py -d /path/to/project_directory
```
* To enable IMC switch list autoupdating run the program with the '-u' flag
```
python3 python_zeros.py -u
```
Note: if you do not use the '-u' flag then you will have to manually update `completed_devices_list`
* If you do not have a `database.pickle` file already in the project directory then you can run
```
python3 python_zeros.py -l /path/to/raw_files
```
to populate the `database.pickle` file with raw output files. Note: This command is unstable and needs to be used in a directory that only contains correctly formatted raw output files
* Logs of the project can be found in the `logs/` folder

## Structure of the project
* `python_zeros.py` is the main part of the program which calls on other files to run

* `config.json` is the configuration file for entering credential information for switch login, email authentication, and IMC login information if applicable. The config.json file also has a field for specifying the recipient of the automated email generated by the project

* `logs/` is a folder that contains logs of all previous runs of the project

* `output/` is a folder that has the raw output of the 'show' command run on all switches previously

* `completed_devices_file` is a raw text file with all switch IP addresses

* `database.pickle` is a database stored by python in the .pickle format. For more information on Pickle please reference [this page](https://docs.python.org/3/library/pickle.html)

* `requirements.txt` is a file that specifies all dependencies that the project has. You can update all dependencies by running the command below
```
pip3 install -r requirements.txt
```

* `src/datastructures.py` contains classes for Database and Switch datastructures. Each run of the project will load `database.pickle` as a Database and save it to the same file before exiting. The Database class will instantiate Switch instances for every switch found on IMC

* `src/emailhandler` contains the EmailHandler class which uses credentials specified in the config file and handles the automated email generated by the project

* `src/querryimc.py` contains all code related to authenticating to and querrying IMC for automatic updating of `completed_devices_file`
* `src/switchquerrier` handles all communications with network switches to gather information from the 'show' command and has static methods to handle the updating of `completed_devices_file`

## Contributors
* Andy Gregory
* Bond Alexander
