import argparse
import importlib
import os
from typing import Callable, Optional, Any

import sys

from devilsmachine.configdata import ConfigData
from devilsmachine.configparser import ConfigParser
from devilsmachine.module import Module


def make_argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', '-c', required=True, help='Path to config file')
    parser.add_argument('--action', '-a', choices=['list_output_files', 'process'], required=True, help='Action to execute')
    parser.add_argument('--input_root', '--ir', required=True, help='Root directory for input files')
    parser.add_argument('--output-root', '--or', required=True, help='Root directory for output files')
    parser.add_argument('input_file', help='Input file to operate on')
    return parser


def main() -> int:
    parser = make_argparser()
    args = parser.parse_args()
    config = get_config(args.config)
    module = get_module(args.input_file, config)
    if module is None:
        return 1
    action = get_action(args.action)
    action(module, args)
    return 0


def get_module(input_filename: str, config: ConfigData) -> Optional[Module]:
    _, extension = os.path.splitext(input_filename)
    extension = extension[1:]  # Remove dot from beginning
    module_name = config.module_map.get(extension)
    if module_name is None:
        sys.stderr.write('Cannot find module for extension "{0}".\n'.format(extension))
        return None

    seperator_pos = module_name.find(':')
    py_module_name = module_name[:seperator_pos]
    module_class = module_name[seperator_pos+1:]

    py_module = importlib.import_module(py_module_name)
    clazz = getattr(py_module, module_class, None)

    if clazz is None:
        return None

    module = clazz()
    return module


def get_config(filename: str) -> ConfigData:
    config = ConfigData()
    parser = ConfigParser()
    with open(filename) as f:
        source = f.read()
    parser.parse(source, config)
    return config


def get_action(name: str) -> Callable[[Module, Any], int]:
    if name == 'list_output_files':
        return list_output_files
    if name == 'process':
        return process


def list_output_files(module: Module, args) -> int:
    rel_path = os.path.relpath(args.input_file, args.input_root)
    output_files = module.get_output_files(rel_path)
    absolute_paths = []
    for path in output_files:
        absolute_paths.append(os.path.normpath(os.path.join(args.output_root, path)))
    print(';'.join(absolute_paths))
    return 0


def process(module: Module, args) -> int:
    if args.output_root is None or len(args.output_root) == 0:
        sys.stderr.write('--output-root must be defined for process action.\n')
        return 1
    rel_path = os.path.relpath(args.input_file, args.input_root)
    return module.process(rel_path, args.input_root, args.output_root)
