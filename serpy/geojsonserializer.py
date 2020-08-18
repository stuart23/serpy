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
            # In attrs, the key is the field name, and the value is the field
            # type, but for _compile_field_to_tuple, we need the first argument
            # to be the field type, and the second one to be the field name.
            geometry_field = geometry_fields[0][::-1]
            del attrs[geometry_field[1]]

        real_cls = super(GeoJSONSerializerMeta, cls)\
            .__new__(cls, name, bases, attrs)
        if geometry_field:
            real_cls._compiled_geometry_field = _compile_field_to_tuple(
                *geometry_field, serializer_cls=real_cls)
        return real_cls


class GeoJSONSerializer(six.with_metaclass(GeoJSONSerializerMeta, Serializer)):
    altitude_field = None

    def _serialize(self, instance, fields, geometry_field):
        properties = super(GeoJSONSerializer, self)\
            ._serialize(instance, fields)
        geometry = super(GeoJSONSerializer, self)\
            ._serialize(instance, [geometry_field])
        return {
            "type": "Feature",
            "properties": properties,
            "geometry": {
                "type": geometry_field.feature_type,
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
                "type": geometry_field.feature_type,
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
            features = [serialize(instance, fields)]
        return {
            "type": "FeatureCollection",
            "crs": {"type": "name", "properties": {"name": "EPSG:4326"}},
            "features": features
            }
