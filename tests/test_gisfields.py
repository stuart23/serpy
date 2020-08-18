from .obj import Obj
from serpy.gisfields import (PointField)
import unittest


class TestGISFields(unittest.TestCase):
    def test_point_field(self):
        field = PointField()
        self.assertEqual(field.to_value(Obj(tuple=(1, 2, 3))), (1, 2, 3))
        self.assertEqual(field.to_value(Obj(tuple=(-4, -5, -6))), (-4, -5, -6))
