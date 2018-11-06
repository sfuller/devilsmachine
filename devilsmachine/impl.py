import importlib
import os
import subprocess
from typing import Callable, Optional, Set, List
import sys

import devilsmachine.args
from devilsmachine import stockmodules, Action
from devilsmachine.args import ArgumentData
from devilsmachine.configdata import ConfigData
from devilsmachine.configparser import ConfigParser
from devilsmachine.machine import Machine
from devilsmachine.module import Module


def main() -> int:
    args = ArgumentData()

    # noinspection PyTypeChecker
    devilsmachine.args.argparser.parse_args(namespace=args)

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


def get_action(action: Action) -> Callable[[ArgumentData], int]:
    if action is Action.LIST_OUTPUT_FILES:
        return list_output_files
    if action is Action.PROCESS:
        return process
    if action is Action.UPDATE_DEPENDENCIES:
        return update_dependencies
    if action is Action.LIST_TOOLS:
        return list_tools


def list_output_files(args: ArgumentData) -> int:
    config = get_config(args.config)
    output_files: List[str] = []

    for input_file in args.input_files:
        module = get_module(input_file, config)
        if module is None:
            return 1
        rel_path = os.path.relpath(input_file, args.input_root)
        output_files.extend(module.get_output_files(rel_path))

    absolute_paths = []
    for path in output_files:
        absolute_paths.append(os.path.normpath(os.path.join(args.output_root, path)))
    sys.stdout.write(';'.join(absolute_paths))
    return 0


def process(args: ArgumentData) -> int:
    config = get_config(args.config)
    machine = Machine(args.tools)

    for input_file in args.input_files:
        module = get_module(input_file, config)
        if module is None:
            return 1
        if args.output_root is None or len(args.output_root) == 0:
            sys.stderr.write('--output-root must be defined for process action.\n')
            return 1
        rel_path = os.path.relpath(input_file, args.input_root)
        return module.process(machine, rel_path, args.input_root, args.output_root)


def update_dependencies(args: ArgumentData) -> int:
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


def list_tools(args: ArgumentData) -> int:
    config = get_config(args.config)
    required_tools: Set[str] = set()
    for input_file in args.input_files:
        module = get_module(input_file, config)
        required_tools.update(module.get_required_tools())

    sys.stdout.write(';'.join(required_tools))
    return 0
