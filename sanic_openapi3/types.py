import json

from datetime import date, time, datetime
from typing import List, Dict, Any, get_type_hints


class Definition:
    __fields: dict

    def __init__(self, **kwargs):
        self.__fields = self.guard(kwargs)

    @property
    def fields(self):
        return self.__fields

    def guard(self, fields):
        return {k: v for k, v in fields.items() if k in properties(self).keys()}

    def serialize(self):
        return serialize(self.fields)

    def __str__(self):
        return json.dumps(self.serialize())


class Schema(Definition):
    type: str
    format: str
    description: str
    nullable: False
    default: None
    example: None
    oneOf: List[Definition]
    anyOf: List[Definition]
    allOf: List[Definition]

    @staticmethod
    def make(value):
        if isinstance(value, Schema):
            return value

        if value == bool:
            return Boolean()
        elif value == int:
            return Integer()
        elif value == float:
            return Float()
        elif value == str:
            return String()
        elif value == bytes:
            return Byte()
        elif value == bytearray:
            return Binary()
        elif value == date:
            return Date()
        elif value == time:
            return Time()
        elif value == datetime:
            return DateTime()

        _type = type(value)

        if _type == bool:
            return Boolean(default=value)
        elif _type == int:
            return Integer(default=value)
        elif _type == float:
            return Float(default=value)
        elif _type == str:
            return String(default=value)
        elif _type == bytes:
            return Byte(default=value)
        elif _type == bytearray:
            return Binary(default=value)
        elif _type == date:
            return Date()
        elif _type == time:
            return Time()
        elif _type == datetime:
            return DateTime()
        elif _type == list:
            if len(value) == 0:
                schema = Schema(nullable=True)
            elif len(value) == 1:
                schema = Schema.make(value[0])
            else:
                schema = Schema(oneOf=[Schema.make(x) for x in value])

            return Array(schema)
        elif _type == dict:
            return Object({k: Schema.make(v) for k, v in value.items()})
        else:
            return Object({k: Schema.make(v) for k, v in properties(value).items()})


class Boolean(Schema):
    def __init__(self, **kwargs):
        super().__init__(type="boolean", **kwargs)


class Integer(Schema):
    def __init__(self, **kwargs):
        super().__init__(type="integer", format="int32", **kwargs)


class Long(Schema):
    def __init__(self, **kwargs):
        super().__init__(type="integer", format="int64", **kwargs)


class Float(Schema):
    def __init__(self, **kwargs):
        super().__init__(type="number", format="float", **kwargs)


class Double(Schema):
    def __init__(self, **kwargs):
        super().__init__(type="number", format="double", **kwargs)


class String(Schema):
    def __init__(self, **kwargs):
        super().__init__(type="string", **kwargs)


class Byte(Schema):
    def __init__(self, **kwargs):
        super().__init__(type="string", format="byte", **kwargs)


class Binary(Schema):
    def __init__(self, **kwargs):
        super().__init__(type="string", format="binary", **kwargs)


class Date(Schema):
    def __init__(self, **kwargs):
        super().__init__(type="string", format="date", **kwargs)


class Time(Schema):
    def __init__(self, **kwargs):
        super().__init__(type="string", format="time", **kwargs)


class DateTime(Schema):
    def __init__(self, **kwargs):
        super().__init__(type="string", format="date-time", **kwargs)


class Password(Schema):
    def __init__(self, **kwargs):
        super().__init__(type="string", format="password", **kwargs)


class Email(Schema):
    def __init__(self, **kwargs):
        super().__init__(type="string", format="email", **kwargs)


class Object(Schema):
    properties: Dict[str, Schema]

    def __init__(self, properties: Dict[str, Schema]=None, **kwargs):
        super().__init__(type="object", properties=properties or {}, **kwargs)


class Array(Schema):
    items: Schema

    def __init__(self, items: Schema, **kwargs):
        super().__init__(type="array", items=items, **kwargs)


def serialize(value) -> Any:
    if isinstance(value, Definition):
        return value.serialize()

    if isinstance(value, dict):
        return {k: serialize(v) for k, v in value.items()}

    if isinstance(value, list):
        return [serialize(v) for v in value]

    return value


def properties(value: object) -> Dict:
    fields = {x: v for x, v in value.__dict__.items() if not x.startswith('_')}

    return {**get_type_hints(value.__class__), **fields}
