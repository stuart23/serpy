import six

from .serializer import _compile_field_to_tuple, Serializer, SerializerMeta
from .gisfields import GeometryField


class GeoJSONSerializerMeta(SerializerMeta):
    def __new__(cls, name, bases, attrs):
        # If the class is just GeoJSONSerializer, then there will not be any
        # geometry field. Otherwise ensure there is a GeometryField
        if name == 'GeoJSONSerializer':
            return super(GeoJSONSerializerMeta, cls)\
                .__new__(cls, name, bases, attrs)
        geometry_fields = list(
            filter(lambda attr: isinstance(attr[1], GeometryField),
                   attrs.items())
            )
        if len(geometry_fields) > 1:
            raise TypeError(
                'Only one GeometryField must be defined for each '
                'GeoJSONSerializer'
                )
        elif len(geometry_fields) == 0:
            raise TypeError(
                'A GeometryField must be defined for the GeoJSONSerializer'
                )
        else:
            geometry_field_name, geometry_field = geometry_fields[0]
            del attrs[geometry_field_name]

        real_cls = super(GeoJSONSerializerMeta, cls)\
            .__new__(cls, name, bases, attrs)
        real_cls._compiled_geometry_field = _compile_field_to_tuple(
            geometry_field, geometry_field_name, serializer_cls=real_cls
            )
        real_cls.geometry_feature_type = geometry_field.feature_type
        return real_cls


class GeoJSONSerializer(six.with_metaclass(GeoJSONSerializerMeta, Serializer)):
    altitude_field = None

    def _serialize(self, instance, fields, geometry_field):
        properties = super(GeoJSONSerializer, self)\
            ._serialize(instance, fields)
        (_, geometry), = super(GeoJSONSerializer, self)\
            ._serialize(instance, [geometry_field]).items()
        return {
            "type": "Feature",
            "properties": properties,
            "geometry": {
                "type": self.geometry_feature_type,
                "coordinates": geometry
            }
        }

    def _serialize_with_altitude(self, instance, fields, geometry_field):
        '''
        Returns a method for serializing points using a specified field for the
        altitude 'z' component.
        '''
        properties = super(GeoJSONSerializer, self)\
            ._serialize(instance, fields)
        (_, geometry), = super(GeoJSONSerializer, self)\
            ._serialize(instance, [geometry_field]).items()
        altitude = properties[self.altitude_field]
        return {
            "type": "Feature",
            "properties": properties,
            "geometry": {
                "type": self.geometry_feature_type,
                "coordinates": geometry + (altitude,)
            }
        }

    def to_value(self, instance):
        fields = self._compiled_fields
        if self.altitude_field:
            serialize = self._serialize_with_altitude
        else:
            serialize = self._serialize
        geometry_field = self._compiled_geometry_field
        if self.many:
            features = [serialize(o, fields, geometry_field) for o in instance]
        else:
            features = [serialize(instance, fields, geometry_field)]
        return {
            "type": "FeatureCollection",
            "crs": {"type": "name", "properties": {"name": "EPSG:4326"}},
            "features": features
            }
