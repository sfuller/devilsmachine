from typing import Dict, Iterable


class Machine(object):
    """
    The interface to devilsmachine functionality from a module.
    """

    def __init__(self, tool_args: Iterable[str]) -> None:
        self.tools: Dict[str, str] = {}
        for arg in tool_args:
            parts = arg.split('=', maxsplit=2)
            if len(parts) < 2:
                continue
            self.tools[parts[0]] = parts[1]

    def get_tool_path(self, name: str) -> str:
        if name not in self.tools:
            raise ValueError('Undefined tool "{0}". This is a either a devilsmachinie bug or a bug in a ' 
                             'postprocessor module')
        return self.tools[name]
