# zeros
This project is used by the networking team to identify network switch ports that have been innactive for 90+ days

## Running the code
* You can download this code by running `git clone https://github.com/BondAlexander/zeros.git`
* Next install all dependencies by running `pip3 install -r requirements.txt`
* Once the code is downloaded you will need to fill out the credentials in 'auth.json'. The IMC section must have credentials that are authorized for the IMC server. The SSH section must be filled out with user credentials that are authorized remote access to all the network switches 
* To run the code itself you can type `python3 python_zeros.py`
* The program will output a file containing the full output from all switches registered on IMC
