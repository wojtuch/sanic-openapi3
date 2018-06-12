from collections import defaultdict
from typing import Any
from openapitools import Schema, ComponentsBuilder, SpecificationBuilder, OperationBuilder
from openapitools.definitions import SecurityScheme


class OperationsBuilder(defaultdict):
    def __init__(self):
        super().__init__(OperationBuilder)


_components = ComponentsBuilder()
_operations = OperationsBuilder()
_specification = SpecificationBuilder(_components)


def scheme(_name: str = None):
    def inner(cls):
        _components.scheme(_name or cls.__name__, Schema.make(cls))
        return cls
    return inner


def security(_type: str, _name: str = None, **kwargs):
    def inner(cls: type):
        _components.security(_name or cls.__name__, SecurityScheme.make(_type, cls, **kwargs))
        return cls
    return inner


def operation(name: str):
    def inner(func):
        _operations[func].name(name)
        return func
    return inner


def summary(text: str):
    def inner(func):
        _operations[func].describe(summary=text)
        return func
    return inner


def description(text: str):
    def inner(func):
        _operations[func].describe(description=text)
        return func
    return inner


def document(url: str, description: str = None):
    def inner(func):
        _operations[func].document(url, description)
        return func
    return inner


def tag(*args: str):
    def inner(func):
        _operations[func].tag(*args)
        return func
    return inner


def deprecated():
    def inner(func):
        _operations[func].deprecate()
        return func
    return inner


def body(content: Any, **kwargs):
    def inner(func):
        _operations[func].body(_components.maybe_ref(content), **kwargs)
        return func
    return inner


def parameter(name: str, schema: Any, location: str = 'query', **kwargs):
    def inner(func):
        _operations[func].parameter(name, _components.maybe_ref(schema), location, **kwargs)
        return func
    return inner


def response(status, content: Any = None, description: str = None, **kwargs):
    def inner(func):
        _operations[func].response(status, _components.maybe_ref(content), description, **kwargs)
        return func
    return inner


def secured(*args, **kwargs):
    def inner(func):
        _operations[func].secured(*args, **kwargs)
        return func
    return inner
