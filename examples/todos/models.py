from datetime import date
from sanic_openapi3 import openapi


@openapi.security('apiKey')
class TodoApiKey:
    name = 'x-api-key'
    location = 'header'


@openapi.scheme
class Todo:
    id = int
    done = bool
    text = str
    title = str
    deadline = date


@openapi.scheme
class TodoList:
    limit = int
    items = [Todo]
