import argparse
from typing import List

from devilsmachine import Action

argparser = argparse.ArgumentParser()
argparser.add_argument('--config', '-c', required=True, help='Path to config file')
argparser.add_argument('--action', '-a', type=Action, required=True, help='Action to execute')
argparser.add_argument('--input-root', '--ir', help='Root directory for input files')
argparser.add_argument('--output-root', '--or', help='Root directory for output files')
argparser.add_argument('--input-file', dest='input_files', action='append', help='Specify an input file to operate on')
argparser.add_argument('--venv-dummy-file', help='Path to the dummy file to touch when updating the venv')
argparser.add_argument('--tool', dest='tools', action='append', help='Specify the path to a tool')


class ArgumentData(object):
    def __init__(self) -> None:
        self.config = ''
        self.action = Action.NOOP
        self.input_root = ''
        self.output_root = ''
        self.input_files: List[str] = []
        self.venv_dummy_file = ''
        self.tools: List[str] = []
