import argparse
import enum
import importlib
import os
import subprocess
from typing import Callable, Optional, Any
import sys

from devilsmachine import stockmodules
from devilsmachine.configdata import ConfigData
from devilsmachine.configparser import ConfigParser
from devilsmachine.module import Module


class Action(enum.Enum):
    LIST_OUTPUT_FILES = 'list_output_files'
    PROCESS = 'process'
    UPDATE_DEPENDENCIES = 'update_dependencies'


def make_argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', '-c', required=True, help='Path to config file')
    parser.add_argument('--action', '-a', type=Action, required=True, help='Action to execute')
    parser.add_argument('--input-root', '--ir', help='Root directory for input files')
    parser.add_argument('--output-root', '--or', help='Root directory for output files')
    parser.add_argument('--input-file', help='Input file to operate on')
    parser.add_argument('--venv-dummy-file', help='Path to the dummy file to touch when updating the venv')
    return parser


def main() -> int:
    parser = make_argparser()
    args = parser.parse_args()
    action = get_action(args.action)
    return action(args)


def get_module(input_filename: str, config: ConfigData) -> Optional[Module]:
    _, extension = os.path.splitext(input_filename)

    # Do nothing for modules with no extension
    if not extension:
        return stockmodules.NoOp()

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
        sys.stderr.write(
            'Cannot load module: py_module_name: {0}, module_class: {1}'.format(py_module_name, module_class))
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


def get_action(action: Action) -> Callable[[Any], int]:
    if action is Action.LIST_OUTPUT_FILES:
        return list_output_files
    if action is Action.PROCESS:
        return process
    if action is Action.UPDATE_DEPENDENCIES:
        return update_dependencies


def list_output_files(args) -> int:
    config = get_config(args.config)
    module = get_module(args.input_file, config)
    if module is None:
        return 1
    rel_path = os.path.relpath(args.input_file, args.input_root)
    output_files = module.get_output_files(rel_path)
    absolute_paths = []
    for path in output_files:
        absolute_paths.append(os.path.normpath(os.path.join(args.output_root, path)))
    print(';'.join(absolute_paths))
    return 0


def process(args) -> int:
    config = get_config(args.config)
    module = get_module(args.input_file, config)
    if module is None:
        return 1
    if args.output_root is None or len(args.output_root) == 0:
        sys.stderr.write('--output-root must be defined for process action.\n')
        return 1
    rel_path = os.path.relpath(args.input_file, args.input_root)
    return module.process(rel_path, args.input_root, args.output_root)


def update_dependencies(args) -> int:
    config = get_config(args.config)

    if len(config.dependencies) == 0:
        return 0

    executable = sys.executable
    pip_args = [executable, '-m', 'pip', 'install']
    for dependency in config.dependencies:
        pip_args.append(dependency)

    result = subprocess.run(pip_args)
    if result.returncode is not 0:
        return result.returncode

    # Touch dummy file
    with open(args.venv_dummy_file, 'a'):
        pass
    os.utime(args.venv_dummy_file, None)

    return 0
