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

    def test_just_geometry(self):
        class ASerializer(GeoJSONSerializer):
            a = PointField()

        instance = Obj(a=Obj(tuple=(1, 2, 3)))
        self.assertEqual(
            ASerializer(instance).data,
            {'type': 'FeatureCollection',
             'crs': {'type': 'name', 'properties': {'name': 'EPSG:4326'}},
             'features': [
                {'type': 'Feature',
                 'properties': {},
                 'geometry': {'type': 'Point', 'coordinates': (1, 2, 3)}
                 }
                ]
             }
            )

    def test_with_properties(self):
        class ASerializer(GeoJSONSerializer):
            a = PointField()
            b = Field()

        instance = Obj(a=Obj(tuple=(1, 2, 3)), b='Home')
        self.assertEqual(
            ASerializer(instance).data,
            {'type': 'FeatureCollection',
             'crs': {'type': 'name', 'properties': {'name': 'EPSG:4326'}},
             'features': [
                {'type': 'Feature',
                 'properties': {'b': 'Home'},
                 'geometry': {'type': 'Point', 'coordinates': (1, 2, 3)}
                 }
                ]
             }
            )

    def test_many_geometry(self):
        class ASerializer(GeoJSONSerializer):
            a = PointField()

        instances = [
            Obj(a=Obj(tuple=(1, 2, 3))),
            Obj(a=Obj(tuple=(4, 5, 6)))
            ]
        self.assertEqual(
            ASerializer(instances, many=True).data,
            {'type': 'FeatureCollection',
             'crs': {'type': 'name', 'properties': {'name': 'EPSG:4326'}},
             'features': [
                {'type': 'Feature',
                 'properties': {},
                 'geometry': {'type': 'Point', 'coordinates': (1, 2, 3)}
                 },
                {'type': 'Feature',
                 'properties': {},
                 'geometry': {'type': 'Point', 'coordinates': (4, 5, 6)}
                 }
                ]
             }
            )

    def test_many_geometry(self):
        class ASerializer(GeoJSONSerializer):
            a = PointField()
            b = Field()

        instances = [
            Obj(a=Obj(tuple=(1, 2, 3)), b='Home'),
            Obj(a=Obj(tuple=(4, 5, 6)), b='Work')
            ]
        self.assertEqual(
            ASerializer(instances, many=True).data,
            {'type': 'FeatureCollection',
             'crs': {'type': 'name', 'properties': {'name': 'EPSG:4326'}},
             'features': [
                {'type': 'Feature',
                 'properties': {'b': 'Home'},
                 'geometry': {'type': 'Point', 'coordinates': (1, 2, 3)}
                 },
                {'type': 'Feature',
                 'properties': {'b': 'Work'},
                 'geometry': {'type': 'Point', 'coordinates': (4, 5, 6)}
                 }
                ]
             }
            )
if __name__ == '__main__':
    unittest.main()
