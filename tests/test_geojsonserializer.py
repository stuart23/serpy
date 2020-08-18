import unittest

from .obj import Obj
from serpy.fields import Field
from serpy.gisfields import PointField
from serpy.geojsonserializer import GeoJSONSerializer


class TestGeoJSONSerializer(unittest.TestCase):

    def test_no_geometry(self):
        with self.assertRaises(TypeError):
            class ASerializer(GeoJSONSerializer):
                a = Field()

    def test_simple(self):
        class ASerializer(GeoJSONSerializer):
            a = PointField()

    def test_multiple_geometry(self):
        with self.assertRaises(TypeError):
            class ASerializer(GeoJSONSerializer):
                a = PointField()
                b = PointField()

if __name__ == '__main__':
    unittest.main()
