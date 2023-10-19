import json, os
from pathlib import Path

import sys
sys.path.append('.')


def sql_obj_to_dict(sql_obj):
    d = dict()
    for col in sql_obj.__table__.columns:
        d[col.name] = getattr(sql_obj, col.name)
    return d


def sql_obj_list_to_dict_list(sql_obj_list):
    return [sql_obj_to_dict(sql_obj) for sql_obj in sql_obj_list]


def bytes2dict(b):
    return json.loads(b.decode('utf-8'))


def config_setup(APP_DIR, APP_CACHE_PATH):
    if not APP_CACHE_PATH.is_file():
        if not os.path.isdir(APP_DIR):
            os.makedirs(APP_DIR)
        # APP_DIR_PATH.mkdir(parents=True, exist_ok=True)
            

def read_json(fpath):
    with open(fpath, 'r') as f:
        data = json.load(f)
        return data
    
def write_json(fpath, data):
    with open(fpath, 'w') as f:
        json.dump(data, f)
        

def cache_team_id(app_dir, cache: dict):
    target_path = Path(app_dir) / 'team_id_cache.json'
    write_json(target_path, cache)
    

def read_team_id(app_dir):
    target_path = Path(app_dir) / 'team_id_cache.json'    
    return read_json(target_path)   


def cache_alarm_id(app_dir, cache: dict):
    target_path = Path(app_dir) / 'alarm_id_cache.json'
    write_json(target_path, cache)
    

def read_alarm_id(app_dir, alarm_id: int):
    target_path = Path(app_dir) / 'alarm_id_cache.json'
    data = read_json(target_path)
    for key in data.keys():
        if key == str(alarm_id):
            return data[str(alarm_id)]

    return None
