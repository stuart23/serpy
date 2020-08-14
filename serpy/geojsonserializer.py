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

    def _serialize(self, instance, fields, geometry_field):
        properties = super()._serialize(instance, fields)
        geometry = super()._serialize(instance, [geometry_field])
        return {
            "type": "Feature",
            "properties": properties,
            "geometry": geometry
        }

    def to_value(self, instance):
        fields = self._compiled_fields
        # altitude_field
        import pdb; pdb.set_trace()
        geometry_field = self._compiled_geometry_field
        if self.many:
            serialize = self._serialize
            features = [serialize(o, fields, geometry_field) for o in instance]
        else:
            features = [self._serialize(instance, fields)]
        return {
            "type": "FeatureCollection",
            "crs": {"type": "name", "properties": {"name": "EPSG:4326"}},
            "features": features
            }
