from datetime import date
from sanic_openapi3 import component


@component.security('apiKey')
class TodoApiKey:
    name = 'x-api-key'
    location = 'header'


@component.scheme
class Todo:
    id = int
    done = bool
    text = str
    title = str
    deadline = date


@component.scheme
class TodoList:
    limit = int
    items = [Todo]
