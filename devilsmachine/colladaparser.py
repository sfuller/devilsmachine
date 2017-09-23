from typing import List, Tuple

import collada
import collada.polylist
import collada.primitive
import collada.triangleset

from devilsmachine.data import Buffer, VAOData, VBOAttributesData, AttributeData, GiygasData
from devilsmachine.vertex import Vertex


class ColladaParser(object):
    def __init__(self):
        self.unique_vertecies: List(Vertex) = []
        self.elements: List(int) = []

        self.current_positions = None
        self.current_normals = None
        self.current_uvs = None

    def add_primitive(self, primitive: collada.primitive.Primitive):
        triangleset = primitive
        if isinstance(primitive, collada.polylist.Polylist):
            triangleset = primitive.triangleset()
        elif not isinstance(primitive, collada.triangleset.TriangleSet):
            raise Exception('unsupported primitive')

        pos_indices = triangleset.vertex_index
        norm_indices = triangleset.normal_index
        uv_indices = triangleset.texcoord_indexset[0]
        self.current_positions = triangleset.vertex
        self.current_normals = triangleset.normal
        self.current_uvs = triangleset.texcoordset[0]
        triangle_count = len(pos_indices)

        for i in range(triangle_count):
            self.process_vertex(pos_indices[i][0], norm_indices[i][0], uv_indices[i][0])
            self.process_vertex(pos_indices[i][1], norm_indices[i][1], uv_indices[i][1])
            self.process_vertex(pos_indices[i][2], norm_indices[i][2], uv_indices[i][2])

    def process_vertex(self, pos_index, norm_index, uv_index):
        vertex = Vertex()
        pos = self.current_positions[pos_index]
        normal = self.current_normals[norm_index]
        uv = self.current_uvs[uv_index]
        vertex.posx = pos[0]
        vertex.posy = pos[1]
        vertex.posz = pos[2]
        vertex.normx = normal[0]
        vertex.normy = normal[1]
        vertex.normz = normal[2]
        vertex.tcu = uv[0]
        vertex.tcv = uv[1]

        has_vertex, index = self.has_vertex(vertex)
        if has_vertex:
            self.elements.append(index)
        else:
            self.elements.append(len(self.unique_vertecies))
            self.unique_vertecies.append(vertex)

    def has_vertex(self, vert: Vertex) -> Tuple[bool, int]:
        for i, unique_vert in enumerate(self.unique_vertecies):
            if vert.is_same(unique_vert):
                return True, i
        return False, 0

    def build_data(self) -> GiygasData:
        data = GiygasData()
        vbo = Buffer()
        ebo = Buffer()
        vao = VAOData()

        for vert in self.unique_vertecies:
            vbo.data.append(vert.posx)
            vbo.data.append(vert.posy)
            vbo.data.append(vert.posz)
            vbo.data.append(vert.normx)
            vbo.data.append(vert.normy)
            vbo.data.append(vert.normz)
            vbo.data.append(vert.tcu)
            vbo.data.append(vert.tcv)

        for element in self.elements:
            ebo.data.append(element)

        vbo_attribs = VBOAttributesData()
        vbo_attribs.attributes.append(AttributeData(4, 3))  # pos
        vbo_attribs.attributes.append(AttributeData(4, 3))  # normals
        vbo_attribs.attributes.append(AttributeData(4, 2))  # uvs

        vao.vbos.append(vbo_attribs)

        data.vertex_buffers.append(vbo)
        data.element_buffers.append(ebo)
        data.vaos.append(vao)
        return data
