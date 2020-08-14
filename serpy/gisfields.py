from .fields import Field


class PointField(Field):
    '''
    A :class:`Field` that represents a GIS point.

    The serialized object can be any object that defines the coordinates in a
    `tuple` property, e.g. a django.contrib.gis.geos.Point. The coordinates can
    be 2 or 3 dimensional.
    '''
    @staticmethod
    def to_value(geometry):
        # accessing the geometry.ogr.json seems to be the most complete, but
        # also the slowest way of getting the results. Compared to getting the
        # tuple, json was 7.2ms vs 1.2ms for the tuple. Also a single
        # component, e.g. geometry.x, was 7.2ms
        return(geometry.tuple)
