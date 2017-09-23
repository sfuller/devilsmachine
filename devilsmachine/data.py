from typing import List


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


class AttributeData(object):
    def __init__(self, component_size, component_count):
        self.component_size = component_size
        self.component_count = component_count
