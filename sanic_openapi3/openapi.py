import re

from collections import defaultdict
from itertools import repeat
from sanic import Sanic
from sanic.views import CompositionView
from sanic_openapi3.definitions import *


class OperationBuilder:
    tags: List[str]
    summary: str
    description: str
    operationId: str
    requestBody: RequestBody
    externalDocs: ExternalDocumentation
    parameters: List[Parameter]
    responses: Dict[str, Response]
    security: List[Any]
    callbacks: List[str]  # TODO
    deprecated: bool = False

    def __init__(self):
        self.tags = []
        self.parameters = []
        self.security = []
        self.responses = {}


class SpecificationBuilder:
    operations: Dict[Any, OperationBuilder]
    schemas: Dict[str, Definition]
    security: Dict[str, SecurityScheme]

    def __init__(self):
        self.operations = defaultdict(OperationBuilder)
        self.schemas = {}
        self.security = {}

    def maybe_ref(self, content: Any):
        _type = type(content)

        if _type == type and content.__name__ in self.schemas.keys():
            return Reference("#/components/schemas/%s" % content.__name__)

        return content

    def build(self, app: Sanic) -> OpenAPI:
        info = self.build_info(app)
        paths = defaultdict(dict)
        tags = {}

        # --------------------------------------------------------------- #
        # Blueprints
        # --------------------------------------------------------------- #
        for _blueprint in app.blueprints.values():
            if not hasattr(_blueprint, 'routes'):
                continue

            for _route in _blueprint.routes:
                if _route.handler not in self.operations:
                    continue

                _operation = self.operations.get(_route.handler)

                if not _operation.tags:
                    _operation.tags.append(_blueprint.name)

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

            for _method, _handler in method_handlers:
                if _handler not in self.operations:
                    continue

                _operation = self.operations[_handler]

                if not hasattr(_operation, 'operationId'):
                    _operation.operationId = '%s_%s' % (_method.lower(), _route.name)

                for _parameter in _route.parameters:
                    _operation.parameters.append(Factory.parameter(_parameter.name, _parameter.cast, 'path'))

                paths[uri][_method] = _operation.__dict__

        paths = {k: PathItem(**{k1.lower(): Operation(**v1) for k1, v1 in v.items()}) for k, v in paths.items()}

        # --------------------------------------------------------------- #
        # Tags
        # --------------------------------------------------------------- #
        for _operation in self.operations.values():
            for _tag in _operation.tags:
                tags[_tag] = True

        # --------------------------------------------------------------- #
        # Definitions
        # --------------------------------------------------------------- #
        components = Components(schemas=self.schemas, securitySchemes=self.security)

        return OpenAPI(info, paths, tags=[{"name": name} for name in tags.keys()], components=components)

    @staticmethod
    def build_info(app: Sanic) -> Info:
        title = getattr(app.config, 'OPENAPI_TITLE', 'API')
        version = getattr(app.config, 'OPENAPI_VERSION', '1.0.0')
        description = getattr(app.config, 'OPENAPI_DESCRIPTION', None)
        terms = getattr(app.config, 'OPENAPI_TERMS_OF_SERVICE', None)

        license_name = getattr(app.config, 'OPENAPI_LICENSE_NAME', None)
        license_url = getattr(app.config, 'OPENAPI_LICENSE_URL', None)
        license = License(license_name, url=license_url)

        contact_name = getattr(app.config, 'OPENAPI_CONTACT_NAME', None)
        contact_url = getattr(app.config, 'OPENAPI_CONTACT_URL', None)
        contact_email = getattr(app.config, 'OPENAPI_CONTACT_EMAIL', None)
        contact = Contact(name=contact_name, url=contact_url, email=contact_email)

        return Info(title, version, description=description, termsOfService=terms, license=license, contact=contact)


spec = SpecificationBuilder()


def operation(id: str):
    def inner(func):
        spec.operations[func].operationId = id
        return func
    return inner


def summary(text: str):
    def inner(func):
        spec.operations[func].summary = text
        return func
    return inner


def description(text: str):
    def inner(func):
        spec.operations[func].description = text
        return func
    return inner


def documentation(url: str, description: str = None):
    def inner(func):
        spec.operations[func].externalDocs = ExternalDocumentation(url, description)
        return func
    return inner


def tag(*args: str):
    def inner(func):
        for arg in args:
            spec.operations[func].tags.append(arg)
        return func
    return inner


def deprecated():
    def inner(func):
        spec.operations[func].deprecated = True
        return func
    return inner


def body(content: Any, **kwargs):
    def inner(func):
        spec.operations[func].requestBody = Factory.body(spec.maybe_ref(content), **kwargs)
        return func
    return inner


def parameter(name: str, schema: Any, location: str = 'query', **kwargs):
    def inner(func):
        param = Factory.parameter(name, spec.maybe_ref(schema), location, **kwargs)
        spec.operations[func].parameters.append(param)
        return func
    return inner


def response(status, content: Any=None, description: str = None, **kwargs):
    def inner(func):
        spec.operations[func].responses[status] = Factory.response(spec.maybe_ref(content), description, **kwargs)
        return func
    return inner


def secured(*args, **kwargs):
    def inner(func):
        items = {**{k: [] for k in args}, **kwargs}
        gates = {}

        for name, params in items.items():
            gate = name.__name__ if isinstance(name, type) else name
            gates[gate] = params

        spec.operations[func].security.append(gates)
        return func
    return inner
