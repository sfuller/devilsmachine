from typing import Dict, List


class ConfigData(object):

    def __init__(self):
        self.module_map: Dict[str, str] = {}
        self.dependencies: List[str] = []
