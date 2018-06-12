import re

from collections import defaultdict
from itertools import repeat
from typing import Dict, Any
from openapitools import SpecificationBuilder, ComponentsBuilder, OperationBuilder
from openapitools.definitions import Schema, SecurityScheme, OpenAPI
from sanic.blueprints import Blueprint
from sanic.response import json
from sanic.views import CompositionView


class OpenBlueprint:
    blueprint: Blueprint

    _path: str
    _components: ComponentsBuilder
    _operations: Dict[Any, OperationBuilder]
    _specification: SpecificationBuilder
    _openapi: OpenAPI

    def __init__(self):
        self._path = 'openapi.json'
        self._components = ComponentsBuilder()
        self._operations = defaultdict(OperationBuilder)
        self._specification = SpecificationBuilder(self._components)

        self.blueprint = Blueprint('openapi')
        self.blueprint.listeners['before_server_start'].append(self.build_spec)

    def path(self, value: str):
        self._path = value

    def describe(self, title: str, version: str, **kwargs):
        self._specification.describe(title, version, **kwargs)

    def contact(self, name: str, url: str = None, email: str = None):
        self._specification.contact(name, url, email)

    def license(self, name: str, url: str = None):
        self._specification.license(name, url)

    def scheme(self, _name: str = None):
        def inner(cls):
            self._components.scheme(_name or cls.__name__, Schema.make(cls))
            return cls
        return inner

    def security(self, _type: str, _name: str = None, **kwargs):
        def inner(cls: type):
            self._components.security(_name or cls.__name__, SecurityScheme.make(_type, cls, **kwargs))
            return cls
        return inner

    def operation(self, name: str):
        def inner(func):
            self._operations[func].name(name)
            return func

        return inner

    def summary(self, text: str):
        def inner(func):
            self._operations[func].describe(summary=text)
            return func
        return inner

    def description(self, text: str):
        def inner(func):
            self._operations[func].describe(description=text)
            return func
        return inner

    def document(self, url: str, description: str = None):
        def inner(func):
            self._operations[func].document(url, description)
            return func
        return inner

    def tag(self, *args: str):
        def inner(func):
            self._operations[func].tag(*args)
            return func
        return inner

    def deprecated(self):
        def inner(func):
            self._operations[func].deprecate()
            return func
        return inner

    def body(self, content: Any, **kwargs):
        def inner(func):
            self._operations[func].body(self._components.maybe_ref(content), **kwargs)
            return func
        return inner

    def parameter(self, name: str, schema: Any, location: str = 'query', **kwargs):
        def inner(func):
            self._operations[func].parameter(name, self._components.maybe_ref(schema), location, **kwargs)
            return func
        return inner

    def response(self, status, content: Any = None, description: str = None, **kwargs):
        def inner(func):
            self._operations[func].response(status, self._components.maybe_ref(content), description, **kwargs)
            return func
        return inner

    def secured(self, *args, **kwargs):
        def inner(func):
            self._operations[func].secured(*args, **kwargs)
            return func
        return inner

    def build_spec(self, app, loop):
        # --------------------------------------------------------------- #
        # Blueprints
        # --------------------------------------------------------------- #
        for _blueprint in app.blueprints.values():
            if not hasattr(_blueprint, 'routes'):
                continue

            for _route in _blueprint.routes:
                if _route.handler not in self._operations:
                    continue

                operation = self._operations.get(_route.handler)

                if not operation.tags:
                    operation.tag(_blueprint.name)

        # --------------------------------------------------------------- #
        # Operations
        # --------------------------------------------------------------- #
        for _uri, _route in app.router.routes_all.items():
            if '<file_uri' in _uri:
                continue

            handler_type = type(_route.handler)

            if handler_type is CompositionView:
                view = _route.handler
                method_handlers = view.handlers.items()
            else:
                method_handlers = zip(_route.methods, repeat(_route.handler))

            uri = _uri if _uri == "/" else _uri.rstrip('/')

            for segment in _route.parameters:
                uri = re.sub('<' + segment.name + '.*?>', '{' + segment.name + '}', uri)

            for method, _handler in method_handlers:
                if _handler not in self._operations:
                    continue

                operation = self._operations[_handler]

                for _parameter in _route.parameters:
                    operation.parameter(_parameter.name, _parameter.cast, 'path')

                self._specification.operation(uri, method, operation)

        self._openapi = self._specification.build().serialize()

        # --------------------------------------------------------------- #
        # Routes
        # --------------------------------------------------------------- #
        app.add_route(self.spec_json, uri=self._path, strict_slashes=True)

    def spec_json(self, request):
        return json(self._openapi)
