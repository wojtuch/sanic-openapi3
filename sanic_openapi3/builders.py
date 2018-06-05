from sanic_openapi3.definitions import *


class OperationBuilder:
    summary: str
    description: str
    operationId: str
    requestBody: RequestBody
    externalDocs: ExternalDocumentation
    tags: List[str]
    security: List[Any]
    parameters: List[Parameter]
    responses: Dict[str, Response]
    callbacks: List[str]  # TODO
    deprecated: bool = False

    def __init__(self):
        self.tags = []
        self.security = []
        self.parameters = []
        self.responses = {}

    def name(self, value: str):
        self.operationId = value

    def describe(self, summary: str, description: str = None):
        self.summary = summary
        self.description = description

    def document(self, url: str, description: str = None):
        self.externalDocs = ExternalDocumentation(url, description)

    def tag(self, *args: str):
            for arg in args:
                self.tags.append(arg)

    def deprecate(self):
        self.deprecated = True

    def body(self, content: Any, **kwargs):
        self.requestBody = Factory.body(maybe_ref(content), **kwargs)

    def parameter(self, name: str, schema: Any, location: str = 'query', **kwargs):
        param = Factory.parameter(name, maybe_ref(schema), location, **kwargs)
        self.parameters.append(param)

    def response(self, status, content: Any = None, description: str = None, **kwargs):
        self.responses[status] = Factory.response(maybe_ref(content), description, **kwargs)

    def secured(self, *args, **kwargs):
        items = {**{v: [] for v in args}, **kwargs}
        gates = {}

        for name, params in items.items():
            gate = name.__name__ if isinstance(name, type) else name
            gates[gate] = params

        self.security.append(gates)

    def build(self):
        return Operation(**self.__dict__)


class SpecificationBuilder:
    _url: str
    _title: str
    _version: str
    _description: str
    _terms: str
    _contact: Contact
    _license: License
    _tags: Dict[str, Tag]
    _paths: Dict[str, Dict[str, dict]]
    _schemas: Dict[str, Schema]
    _security: Dict[str, SecurityScheme]

    def __init__(self):
        self._tags = {}
        self._paths = {}
        self._schemas = {}
        self._security = {}

    def maybe_ref(self, content: Any):
        if type(content) == type and content.__name__ in self._schemas.keys():
            return Reference("#/components/schemas/%s" % content.__name__)

        return content

    def url(self, value: str):
        self._url = value

    def describe(self, title: str, version: str, description: str = None, terms: str = None):
        self._title = title
        self._version = version
        self._description = description
        self._terms = terms

    def tag(self, name: str, **kwargs):
        self._tags[name] = Tag(name, **kwargs)

    def contact(self, name: str = None, url: str = None, email: str = None ):
        self._contact = Contact(name=name, url=url, email=email)

    def license(self, name: str = None, url: str = None ):
        self._license = License(name, url=url)

    def component(self, section, name: str, value: Schema):
        if section == 'schemas':
            self._schemas[name] = value
        elif section == 'security' and isinstance(value, SecurityScheme):
            self._security[name] = value

    def operation(self, path: str, method: str, operation: OperationBuilder):
        for _tag in operation.tags:
            if _tag not in self._tags:
                self._tags[_tag] = Tag(_tag)

        self._paths[path][method] = operation

    def build(self) -> OpenAPI:
        info = self._build_info()
        tags = self._build_tags()
        paths = self._build_paths()
        components = self._build_components()

        return OpenAPI(info, paths, tags=tags, components=components)

    def _build_info(self) -> Info:
        kwargs = {
            'description': self._description,
            'termsOfService': self._terms,
            'license': self._license,
            'contact': self._contact,
        }

        return Info(self._title, self._version, **kwargs)

    def _build_tags(self):
        return self._tags.values()

    def _build_paths(self):
        paths = {}

        for path, operations in self._paths:
            paths[path] = PathItem(**{k: v.build() for k, v in operations.items()})

        return paths

    def _build_components(self) -> Components:
        return Components(schemas=self._schemas, securitySchemes=self._security)