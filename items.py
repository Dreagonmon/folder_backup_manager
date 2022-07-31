import os, json
from typing import List, Tuple
CONFIG_PATH = "data/config.json"

def _exist_folder_list(folders: List[str]) -> List[int]:
    lst = []
    for i, f in enumerate(folders):
        try:
            if os.path.isdir(f):
                lst.append(f)
        except: pass
    return lst

class RsyncBackupItem:
    def __init__(self, name: str):
        self.name = name
        self.source_folders: List[str] = []
        self.backup_folders: List[str] = []
        self.excludes: List[str] = []
        self.includes: List[str] = []
        self.options: List[str] = []
    
    def get_matched_folders(self) -> Tuple[List[int], List[int]]:
        return (
            _exist_folder_list(self.source_folders),
            _exist_folder_list(self.backup_folders),
        )
    
    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "source_folders": list(self.source_folders),
            "backup_folders": list(self.backup_folders),
            "excludes": list(self.excludes),
            "includes": list(self.includes),
            "options": list(self.options),
        }
    
    @staticmethod
    def from_dict(data: dict) -> 'RsyncBackupItem':
        obj = RsyncBackupItem(data["name"])
        obj.source_folders = list(data["source_folders"])
        obj.backup_folders = list(data["backup_folders"])
        obj.excludes = list(data["excludes"])
        obj.includes = list(data["includes"])
        obj.options = list(data["options"])
        return obj

class Config:
    def __init__(self):
        self.backup_items: List[RsyncBackupItem] = []
    
    def to_dict(self) -> dict:
        return {
            "backup_items": [ i.to_dict() for i in self.backup_items ]
        }

    def save(self, path: str = CONFIG_PATH):
        with open(path, "wt", encoding="utf8") as f:
            json.dump(self.to_dict(), indent=4)

    @staticmethod
    def from_dict(data: dict) -> 'Config':
        obj = Config()
        obj.backup_items = [ RsyncBackupItem.from_dict(d) for d in data["backup_items"] ]
        return obj

    @staticmethod
    def load(path: str = CONFIG_PATH) -> 'Config':
        try:
            with open(path, "rt", encoding="utf8") as f:
                data = json.load(f)
            return Config.from_dict(data)
        except:
            return Config()

__default_config = None
def get_config() -> Config:
    global __default_config
    if __default_config == None:
        __default_config = Config.load()
    return __default_config