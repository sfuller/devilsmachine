import os
import subprocess
from typing import List, Iterable

from devilsmachine.machine import Machine
from devilsmachine.module import Module


class CompileGLSL(Module):
    TOOL_GLSLANGVALIDATOR = 'glslangValidator'

    def get_required_tools(self) -> Iterable[str]:
        return (__class__.TOOL_GLSLANGVALIDATOR,)

    def get_output_files(self, input_file: str) -> List[str]:
        path, _ = os.path.splitext(input_file)
        return [path + '.spv']

    def process(self, machine: Machine, input_file: str, input_root: str, output_root: str) -> int:
        dst_path = os.path.join(output_root, input_file)
        os.makedirs(os.path.dirname(dst_path), exist_ok=True)

        path, _ = os.path.splitext(input_file)
        _, stage_ext = os.path.splitext(path)

        if stage_ext == '.vs':
            stage = 'vert'
        else:
            stage = 'frag'

        output_file = os.path.join(output_root, self.get_output_files(input_file)[0])

        args = [
            machine.get_tool_path(__class__.TOOL_GLSLANGVALIDATOR),
            '-S', stage,
            '-o', output_file,
            '-V',  # Compile for Vulkan
            os.path.join(input_root, input_file)
        ]

        result = subprocess.run(args)
        return result.returncode
