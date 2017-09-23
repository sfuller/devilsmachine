import math


class Vertex(object):
    def __init__(self):
        self.posx = 0.0
        self.posy = 0.0
        self.posz = 0.0
        self.normx = 0.0
        self.normy = 0.0
        self.normz = 0.0
        self.tcu = 0.0
        self.tcv = 0.0

    def is_same(self, other):
        tol = 1e-4
        return math.isclose(self.posx, other.posx, rel_tol=tol) \
            and math.isclose(self.posy, other.posy, rel_tol=tol) \
            and math.isclose(self.posz, other.posz, rel_tol=tol) \
            and math.isclose(self.normx, other.normx, rel_tol=tol) \
            and math.isclose(self.normy, other.normy, rel_tol=tol) \
            and math.isclose(self.normz, other.normz, rel_tol=tol) \
            and math.isclose(self.tcu, other.tcu, rel_tol=tol) \
            and math.isclose(self.tcv, other.tcv, rel_tol=tol)

