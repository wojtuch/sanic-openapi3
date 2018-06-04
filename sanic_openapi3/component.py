from sanic_openapi3.definitions import Factory, SecurityScheme
from sanic_openapi3.openapi import spec


def scheme(cls: type):
    spec.schemas[cls.__name__] = Factory.make(cls)

    return cls


def security(_type: str, **kwargs):
    def inner(cls: type):
        params = cls.__dict__ if hasattr(cls, '__dict__') else {}
        spec.security[cls.__name__] = SecurityScheme(_type, **params, **kwargs)
        return cls
    return inner
