from sanic_openapi3 import openapi
from openapitools.types import *


@openapi.security('apiKey')
class TodoApiKey:
    name = 'x-api-key'
    location = 'header'


@openapi.scheme()
class Todo:
    id = int
    done = bool
    text = str
    title = str


@openapi.scheme()
class TodoList:
    limit = int
    items = Array(Todo, description="List of Todo objects")
