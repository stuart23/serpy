from .fields import Field


class GeometryField(Field):
    '''
    Class exactly the same as the same as :class:`Field` but subclassed so all
    :class:`GeometryField` subclasses can be tested if they are an instance of
    this class.
    '''
    pass


class PointField(GeometryField):
    '''
    A :class:`Field` that represents a GIS point.

    The input object can be any object that defines the coordinates in a
    `tuple` property, e.g. a :class:`django.contrib.gis.geos.Point`. The
    coordinates can be 2 or 3 dimensional.
    '''
    feature_type = 'Point'

    @staticmethod
    def to_value(geometry):
        # accessing the geometry.ogr.json seems to be the most complete, but
        # also the slowest way of getting the results. Compared to getting the
        # tuple, json was 7.2ms vs 1.2ms for the tuple. Also a single
        # component, e.g. geometry.x, was 7.2ms
        return(geometry.tuple)


class PolygonField(GeometryField):
    '''
    A :class:`Field` that represents a GIS polygon.

    The input object can be any object that has a list of a list of coordinates
    as the the `tuple` property, e.g. a
    :class:`django.contrib.gis.geos.Polygon`.
    '''
    feature_type = 'Polygon'

    @staticmethod
    def to_value(geometry):
        return(geometry.tuple)
