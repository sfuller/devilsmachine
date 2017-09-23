import struct
import enum

from devilsmachine import GiygasData
from devilsmachine.data import Buffer, VAOData, VBOAttributesData, AttributeData


class NodeTag(enum.IntEnum):
    NODE_TAG_VBO = 0
    NODE_TAG_EBO = 1
    NODE_TAG_VAO = 2


class GiygasFileBuilder(object):
    def __init__(self, file, data: GiygasData):
        self.file = file
        self.data = data

    def write_bytes(self, bytes) -> None:
        self.file.write(bytes)

    def write(self) -> None:
        # Write magic header
        self.write_bytes('giygas  '.encode('ascii'))
        # Version
        self.write_bytes(struct.pack('I', 0))

        self.write_vbos()
        self.write_ebos()
        self.write_vaos()

    def write_vbos(self) -> None:
        for buffer in self.data.vertex_buffers:
            self.write_vbo(buffer)

    def write_ebos(self) -> None:
        for buffer in self.data.element_buffers:
            self.write_ebo(buffer)

    def write_vaos(self) -> None:
        for vao in self.data.vaos:
            self.write_vao(vao)

    def write_vbo(self, vbo: Buffer) -> None:
        size = len(vbo.data) * 4

        # write tag
        self.write_bytes(struct.pack('I', NodeTag.NODE_TAG_VBO))

        # write size
        self.write_bytes(struct.pack('I', size))

        # write data
        buffer = bytearray(size)
        offset = 0
        for element in vbo.data:
            struct.pack_into('f', buffer, offset, element)
            offset += 4
        self.write_bytes(buffer)

    def write_ebo(self, ebo: Buffer) -> None:
        count = len(ebo.data)
        element_size = 4

        # write tag
        self.write_bytes(struct.pack('I', NodeTag.NODE_TAG_EBO))

        # write count
        self.write_bytes(struct.pack('I', count))

        # write element size
        self.write_bytes(struct.pack('I', element_size))

        # write elements
        buffer = bytearray(count * element_size)
        offset = 0
        for element in ebo.data:
            struct.pack_into('I', buffer, offset, element)
            offset += element_size
        self.write_bytes(buffer)

    def write_vao(self, vao: VAOData) -> None:
        vbo_count = len(vao.vbos)

        # write tag
        self.write_bytes(struct.pack('I', NodeTag.NODE_TAG_VAO))

        # write vbo count
        self.write_bytes(struct.pack('H', vbo_count))

        for vbo in vao.vbos:
            self.write_vao_attributes(vbo)

    def write_vao_attributes(self, attribs: VBOAttributesData) -> None:
        attrib_count = len(attribs.attributes)

        # write attribute count
        self.write_bytes(struct.pack('H', attrib_count))

        for attrib in attribs.attributes:
            self.write_vao_attribute(attrib)

    def write_vao_attribute(self, attrib: AttributeData) -> None:
        self.write_bytes(struct.pack('B', attrib.component_size))
        self.write_bytes(struct.pack('B', attrib.component_count))






