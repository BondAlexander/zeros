# zeros
This project is used by the networking team to identify network switch ports that have been innactive for 90+ days

## Running the code
* You can download this code by running `git clone https://github.com/BondAlexander/zeros.git`
* Next install all dependencies by running `pip3 install -r requirements.txt`
* Next, fill out the credentials in 'auth.json'. The 'IMC' section must have credentials that are authorized for the IMC server. The 'SSH' section must be filled out with user credentials that are authorized remote access to all the network switches. The 'Email' section pertains to the automated emailing. The 'recipient' portion should be the email address that is to receive automated emails
* To run the code itself you can type `python3 python_zeros.py`
* The program will output a file containing the full output from all switches registered on IMC and send the file to the email address specified in auth.json under Email > recipient

## Structure of the code
In the top level directory you have the 'python_zeros.py'. This is the main part of the program which calls on other files to run

All 'helper' code is located in the 'src/' folder and is not meant to be run on its own