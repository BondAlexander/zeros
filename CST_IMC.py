#!/usr/bin/env python3
from auth import IMCAuth
from device import get_all_devs
from netassets import get_dev_asset_details_all
import getpass
import json
from os import system
import time
import re

'''
This code is based off of the CST_IMC project at Colorado State Universities Cybersecurity Internship.
This code was forked 2/28/2022
'''


def authenticate_user(tries=2):
    system("cls")
    uname = input("Username: ")
    passwd= getpass.getpass("Password: ")
    ip = "10.100.201.199"
    port = "8080"
    auth = IMCAuth("http://", str(ip), str(port), uname, passwd)

    if '200' not in str(auth.get_auth()):
        if tries == 0:
            print('Too many attemps. Exiting program.')
            exit()
        print(f'You have {tries} more attempts.')
        time.sleep(2)
        authenticate_user(tries-1)
    print("\t*Connected To IMC Server*")
    return auth

def saveData(data, file_name):
    with open(file_name, "w") as json_file:
        json.dump(data, json_file, indent=4)
    print(f"Saved ICM Data To '{file_name}'")


def formatAsset(asset, componentDict):
    # Add component data of the asset to the top level
    for key in componentDict.keys():
        if key[1] == asset['label']:
            asset.update(componentDict[key])
            pass

    keyValue = [['Owner', 'contact'],
                ['name', 'label'],
                ['asset_tag', 'id'],
                ['MAC', 'mac'],
                ['OS', 'sysDescription'],
                ['IP', 'ip'],
                ['IPMask', 'mask'],
                ['location_name', 'location'],
                ['model_name', 'typeName'],
                ['manufacturer_name', 'mfgName'],
                ['category_name', 'devCategoryImgSrc'],
                ['Serial', 'serialNum'],
                ['BIOS', 'firmwareVersion']]
    newAsset = {
        'Source': 'IMC',
        'status':  2,
        'component': [],
        'custom_fields': {}
    }
    for keys in keyValue:
        newAsset[keys[0]] = re.sub(r'\\|"|\r|\n|\'', " ", asset[keys[1]]) if keys[1] in asset and len(asset[keys[1]]) > 0 else 'UNSPECIFIED'
    newAsset['asset_tag'] = f"IMC:{newAsset['asset_tag']}"

    return newAsset

def createAssets(asset_dict, component_dict):
    dictionary = {}
    for i in asset_dict:
        id = asset_dict[i]['id']
        dictionary[id] = formatAsset(asset_dict[i], component_dict)
    return dictionary

def appendComponent(asset_dict,component_dict):
    keyValue = [['Description', 'desc'],
                ['Relative Position', 'relPos'],
                ['Name', 'name'],
                ['Hard Version', 'hardVersion'],
                ['Soft Version', 'softVersion'],
                ['Serial', 'serialNum'],
                ['Manufacturer', 'mfgName'],
                ['Model', 'model'],
                ['Asset', 'asset']]
    for i in component_dict:
        if component_dict[i]['desc'] == asset_dict[i[0]]['name']:
            continue

        newComponent = {}
        for keys in keyValue:
            newComponent[keys[0]] = re.sub(r'\\|"|\r|\n', " ", component_dict[i][keys[1]]) if keys[1] in component_dict[i] and len(component_dict[i][keys[1]]) > 0 else 'UNSPECIFIED'
        asset_dict[i[0]]['component'].append(newComponent)
    return asset_dict

def formatDict(dict, key, asset=True):
    dictionary = {}
    for item in dict:
        if asset:
            dictionary[item[key]] = item
        else:
            dictionary[(item[key[0]], item[key[1]], item[key[2]])] = item
    return dictionary

#_____Main_________
if __name__ == '__main__':
    authentication_token = authenticate_user()

    asset_dict = formatDict((get_all_devs(authentication_token, "http://10.100.201.199:8080")), 'id')
    print("\tGetting All Device Details...")
    component_dict = formatDict(get_dev_asset_details_all(authentication_token, "http://10.100.201.199:8080"), ('devId', 'desc', 'asset'), asset=False)
    print("\tCreating Assets...")
    combined_dict = createAssets(asset_dict, component_dict)
    print("\tAppending Data to Assets...")
    combined_dict = appendComponent(combined_dict, component_dict)

    saveData(combined_dict, "IMC assets.json")
