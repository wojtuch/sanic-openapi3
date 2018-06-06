from sanic_openapi3.types import Schema
from sanic_openapi3.definitions import SecurityScheme
from sanic_openapi3.main import components


def scheme(_name: str = None):
    def inner(cls):
        components.scheme(_name or cls.__name__, Schema.make(cls))
        return cls
    return inner


def security(_type: str, _name: str = None, **kwargs):
    def inner(cls: type):
        components.security(_name or cls.__name__, SecurityScheme.make(_type, cls, **kwargs))
        return cls
    return inner
