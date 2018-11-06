import shutil
import os
from typing import List

from devilsmachine.machine import Machine
from devilsmachine.module import Module


class Copy(Module):
    def get_output_files(self, input_file: str) -> List[str]:
        return [input_file]

    def process(self, machine: Machine, input_file: str, input_root: str, output_root: str) -> int:
        dst_path = os.path.join(output_root, input_file)
        os.makedirs(os.path.dirname(dst_path), exist_ok=True)
        shutil.copy(os.path.join(input_root, input_file), dst_path)
        return 0


class NoOp(Module):
    def get_output_files(self, input_file: str) -> List[str]:
        return []

    def process(self, machine: Machine, input_file: str, input_root: str, output_root: str) -> int:
        return 0
