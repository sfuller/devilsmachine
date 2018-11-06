import enum


class Action(enum.Enum):
    NOOP = 'noop'
    LIST_OUTPUT_FILES = 'list_output_files'
    LIST_TOOLS = 'list_tools'
    PROCESS = 'process'
    UPDATE_DEPENDENCIES = 'update_dependencies'
