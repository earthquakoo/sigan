import os
import typer
from pathlib import Path
from functools import lru_cache

import sys
sys.path.append('.')


import sigan.utils.general_utils as general_utils


cur_file_dir = os.path.dirname(os.path.realpath(__file__))

class Config:
    def __init__(self):
        self.config = general_utils.read_json(os.path.join(cur_file_dir, "config.json"))
        self.base_url = self.config['base_url']
        self.app_name = self.config['app_name']
        self.app_dir = typer.get_app_dir(self.app_name)
        self.app_dir_path: Path = Path(self.app_dir)
        self.team_id_path: Path = Path(self.app_dir) / "team_id_cache.json"
        self.config_path: Path = Path(self.app_dir) / "config.json"
        self.version = self.config['version']
        
        
@lru_cache()
def get_config():
    return Config()