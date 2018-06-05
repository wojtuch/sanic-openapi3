from collections import defaultdict
from typing import Any
from sanic_openapi3.builders import OperationBuilder, SpecificationBuilder, Factory

operations = defaultdict(OperationBuilder)
specification = SpecificationBuilder()


def operation(name: str, text: str, description: str = None):
    def inner(func):
        operations[func].name(name)
        operations[func].describe(text, description)
        return func
    return inner


def document(url: str, description: str = None):
    def inner(func):
        operations[func].document(url, description)
        return func
    return inner


def tag(*args: str):
    def inner(func):
        operations[func].tag(*args)
    return inner


def deprecated():
    def inner(func):
        operations[func].deprecate()
        return func
    return inner


def body(content: Any, **kwargs):
    def inner(func):
        operations[func].body(content, **kwargs)
        return func
    return inner


def parameter(name: str, schema: Any, location: str = 'query', **kwargs):
    def inner(func):
        operations[func].parameter(name, schema, location, **kwargs)
        return func
    return inner


def response(status, content: Any=None, description: str = None, **kwargs):
    def inner(func):
        operations[func].response(status, content, description, **kwargs)
        return func
    return inner


def secured(*args, **kwargs):
    def inner(func):
        operations[func].secured(*args, **kwargs)
    return inner


def scheme(_name: str = None):
    def inner(cls: type):
        specification.component('security', _name or cls.__name__, Factory.make(cls))
        return cls
    return inner


def security(_type: str, _name: str = None, **kwargs):
    def inner(cls: type):
        specification.component('security', _name or cls.__name__, Factory.security(_type, cls, **kwargs))
        return cls
    return inner
