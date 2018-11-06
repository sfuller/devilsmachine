from typing import List, Iterable

from devilsmachine.machine import Machine


class Module(object):
    def get_required_tools(self) -> Iterable[str]:
        return ()

    def get_output_files(self, input_file: str) -> List[str]:
        pass

    def process(self, machine: Machine, input_file: str, input_root: str, output_root: str) -> int:
        pass
