import six

from .serializer import _compile_field_to_tuple, Serializer, SerializerMeta
from .fields import GeometryField


class GeoJSONSerializerMeta(SerializerMeta):
    def __new__(cls, name, bases, attrs):
        for attr_name, field in attrs.items():
            if isinstance(field, GeometryField):
                geometry_field = (field, attr_name)
                del attrs[attr_name]
                break
        else:
            geometry_field = None
        real_cls = super().__new__(cls, name, bases, attrs)
        if geometry_field:
            real_cls._compiled_geometry_field = _compile_field_to_tuple(
                *geometry_field, real_cls)
        return real_cls


class GeoJSONSerializer(six.with_metaclass(GeoJSONSerializerMeta, Serializer)):
    altitude_field = None

    def _serialize(self, instance, fields, geometry_field):
        properties = super()._serialize(instance, fields)
        geometry = super()._serialize(instance, [geometry_field])
        return {
            "type": "Feature",
            "properties": properties,
            "geometry": {
                "type": "Point",
                "coordinates": geometry
            }
        }

    def _serialize_with_altitude(self, instance, fields, geometry_field):
        '''
        Returns a method for serializing points using a specified field for the
        altitude 'z' component.
        '''
        properties = super()._serialize(instance, fields)
        (_, geometry), = super()._serialize(instance, [geometry_field]).items()
        altitude = properties[self.altitude_field]
        return {
            "type": "Feature",
            "properties": properties,
            "geometry": {
                "type": "Point",
                "coordinates": (*geometry, altitude)
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
            features = [serialize(instance, fields)]
        return {
            "type": "FeatureCollection",
            "crs": {"type": "name", "properties": {"name": "EPSG:4326"}},
            "features": features
            }
