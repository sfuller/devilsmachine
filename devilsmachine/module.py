from typing import List


class Module(object):
    def get_output_files(self, input_file: str) -> List[str]:
        pass

    def process(self, input_file: str, input_root: str, output_root: str) -> int:
        pass
