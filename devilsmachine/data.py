import enum
from typing import List


class AttributeUsageHint(enum.IntEnum):
    NO_HINT = 0
    POSITION = 1
    COLOR = 2
    NORMALS = 3
    TEXTURE_COORDINATES_0 = 4
    TEXTURE_COORDINATES_1 = 5
    TEXTURE_COORDINATES_2 = 6
    TEXTURE_COORDINATES_3 = 7


class GiygasData(object):

    def __init__(self):
        self.vertex_buffers: List(Buffer) = []
        self.element_buffers: List(Buffer) = []
        self.vaos: List(VAOData) = []


class Buffer(object):
    def __init__(self):
        self.data: List(float) = []


class VAOData(object):
    def __init__(self):
        self.vbos: List(VBOAttributesData) = []


class VBOAttributesData(object):
    def __init__(self):
        self.attributes: List(AttributeData) = []
        self.stride: int = 0


class AttributeData(object):
    def __init__(self, component_size: int, component_count: int, offset: int, hint: AttributeUsageHint):
        self.component_size = component_size
        self.component_count = component_count
        self.offset = offset
        self.hint = hint
