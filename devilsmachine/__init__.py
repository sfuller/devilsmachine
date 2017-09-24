import collada
import collada.polylist
import collada.triangleset
import collada.primitive
import argparse

import sys

from devilsmachine.colladaparser import ColladaParser
from devilsmachine.data import GiygasData
from devilsmachine.filebuilder import GiygasFileBuilder


def make_argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument('file')
    return parser


def main() -> int:
    parser = make_argparser()
    args = parser.parse_args()

    doc = collada.Collada(args.file)

    parser = ColladaParser()

    for geo in doc.geometries:
        for primitive in geo.primitives:
            parser.add_primitive(primitive)

    data = parser.build_data()

    filebuilder = GiygasFileBuilder(sys.stdout.buffer, data)
    filebuilder.write()

    return 0

