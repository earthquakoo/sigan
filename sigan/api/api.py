import sys
sys.path.append('.')

import requests

import sigan.utils.display as display
import sigan.utils.general_utils as general_utils
from sigan.config import get_config

cfg = get_config()


def create_alarm(data: dict):
    
    resp = requests.post(
        url=cfg.base_url + "/slack",
        json=data,
    )
    if resp.status_code == 201:
        display.center_print("Alarm added successfully!", type="success")
        alarm = general_utils.bytes2dict(resp.content)
        return alarm
    elif resp.status_code == 400:
        detail = general_utils.bytes2dict(resp.content)['detail']
        display.center_print(detail, type='detail')
    else:
        display.center_print("Error occurred", type='detail')
    exit(0)


def delete_alarm(data: dict):
    
    resp = requests.post(
        cfg.base_url + "/slack/delete",
        json=data,
    )
    if resp.status_code == 200:
        alarm = general_utils.bytes2dict(resp.content)
        display.center_print("Alarm deleted successfully!", type="success")
        return alarm
    elif resp.status_code == 400:
        detail = general_utils.bytes2dict(resp.content)['detail']
        display.center_print(detail, type='detail')
    else:
        display.center_print("Error occurred", type='detail')
    exit(0)


def get_all_alarm(data: dict):
    
    resp = requests.get(
        cfg.base_url + "/slack",
        json=data,
    )
    
    if resp.status_code == 200:
        return general_utils.bytes2dict(resp.content)['alarm']
    elif resp.status_code == 400:
        detail = general_utils.bytes2dict(resp.content)['detail']
        display.center_print(detail, type='detail')
    else:
        display.center_print("Error occurred", type='detail')
    exit(0)


def change_content(data: dict):
    resp = requests.patch(
        cfg.base_url + "/slack/change_content",
        json=data
    )
    if resp.status_code == 200:
        display.center_print("Alarm content changed successfully!", type="success")
        return general_utils.bytes2dict(resp.content)
    elif resp.status_code == 400:
        detail = general_utils.bytes2dict(resp.content)['detail']
        display.center_print(detail, type='detail')
    else:
        display.center_print("Error occurred", type='detail')
    exit(0)
        
        
def change_deadline(data: dict):
    resp = requests.patch(
        cfg.base_url + "/slack/change_deadline",
        json=data
    )
    if resp.status_code == 200:
        display.center_print("Alarm deadline changed successfully!", type="success")
        return general_utils.bytes2dict(resp.content)
    elif resp.status_code == 400:
        detail = general_utils.bytes2dict(resp.content)['detail']
        display.center_print(detail, type='detail')
    else:
        display.center_print("Error occurred", type='detail')
    exit(0)


def change_date(data: dict):
    resp = requests.patch(
        cfg.base_url + "/slack/change_date",
        json=data
    )
    if resp.status_code == 200:
        display.center_print("Alarm date changed successfully!", type="success")
        return general_utils.bytes2dict(resp.content)
    elif resp.status_code == 400:
        detail = general_utils.bytes2dict(resp.content)['detail']
        display.center_print(detail, type='detail')
    else:
        display.center_print("Error occurred", type='detail')
    exit(0)

        
def change_interval(data: dict):
    resp = requests.patch(
        cfg.base_url + "/slack/change_interval",
        json=data
    )
    if resp.status_code == 200:
        display.center_print("Alarm interval changed successfully!", type="success")
        return general_utils.bytes2dict(resp.content)
    elif resp.status_code == 400:
        detail = general_utils.bytes2dict(resp.content)['detail']
        display.center_print(detail, type='detail')
    else:
        display.center_print("Error occurred", type='detail')
    exit(0)
    
    
def register(data: dict):
    resp = requests.post(
        cfg.base_url + "/slack/register",
        json=data
    )
    if resp.status_code == 200:
        display.center_print("Register successfully!", type="success")
        return general_utils.bytes2dict(resp.content)
    elif resp.status_code == 400:
        detail = general_utils.bytes2dict(resp.content)['detail']
        display.center_print(detail, type='detail')
    else:
        display.center_print("Error occurred", type='detail')
    exit(0)