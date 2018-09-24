from typing import Dict, List

from devilsmachine.configdata import ConfigData


class ConfigParser(object):

    def __init__(self):
        pass

    def parse(self, source: str, config: ConfigData):
        source = source.replace('\r', '')
        lines = source.split('\n')

        sections: Dict[str, List[str]] = {}

        current_section_name = ''
        current_section: List[str] = []
        sections[''] = current_section

        def set_section(name: str) -> None:
            nonlocal current_section
            nonlocal current_section_name
            if current_section_name != name:
                current_section = sections.get(name)
                current_section_name = name
                if current_section is None:
                    current_section = []
                    sections[name] = current_section

        for line in lines:
            line = line.strip()
            if len(line) == 0:
                continue
            if line[0] == '#':
                continue

            if line[0] == '[':
                section_name = line[1:-1].strip()
                set_section(section_name)
                continue

            current_section.append(line)

        # Get dependencies
        dependencies_section = sections.get('dependencies', [])
        config.dependencies.extend(dependencies_section)

        # Get processor module mappings
        mappings_sections = sections.get('processors', [])
        for line in mappings_sections:
            left, right = line.split(':', 1)
            left = left.strip()
            right = right.strip()
            config.module_map[left] = right
