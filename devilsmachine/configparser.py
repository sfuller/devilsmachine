from devilsmachine.configdata import ConfigData


class ConfigParser(object):

    def __init__(self):
        pass

    def parse(self, source: str, config: ConfigData):
        source = source.replace('\r', '')
        lines = source.split('\n')

        for line in lines:
            line = line.strip()
            if len(line) == 0:
                continue
            if line[0] == '#':
                continue

            left, right = line.split(':', 1)
            left = left.strip()
            right = right.strip()
            config.module_map[left] = right
