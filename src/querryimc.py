from pyhpeimc.auth import IMCAuth
from pyhpeimc.plat.device import get_all_devs

'''
This code is based off of the CST_IMC project at Colorado State University's Cybersecurity Internship.
This code was forked 2/28/2022
'''


def authenticate_user(ip, port, uname, passwd):
    auth = IMCAuth("http://", str(ip), str(port), uname, passwd)
    if '200' not in str(auth.get_auth()):
        print('Incorrect credentials for IMC server. Exiting...')
        exit(0)
    print("\t*Connected To IMC Server*")
    return auth


def querry_imc(credentials: dict):
    uname = credentials['IMC']['username']
    passwd= credentials['IMC']['password']
    ip = credentials["IMC"]["server"]
    port = credentials["IMC"]["port"]
    authentication_token = authenticate_user(ip, port, uname, passwd)
    new_switch_list = get_all_devs(authentication_token, f"http://{ip}:{port}")
    return new_switch_list
