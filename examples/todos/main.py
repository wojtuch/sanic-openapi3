from sanic import Sanic, Blueprint
from sanic.response import json
from sanic_openapi3 import openapi
from examples.todos.models import TodoList, Todo, TodoApiKey
from examples.todos.data import test_list, test_todo


app = Sanic()
todos = Blueprint('todo', 'todo')


@todos.get("/", strict_slashes=True)
@openapi.summary("Fetches all todos")
@openapi.description("Really gets the job done fetching these todos. I mean, really, wow.")
@openapi.parameter('done', bool)
@openapi.response(200, TodoList)
def todo_list(request):
    return json(test_list)


@todos.get("/<todo_id:int>", strict_slashes=True)
@openapi.summary("Fetches a todo item by ID")
@openapi.response(200, Todo)
def todo_get(request, todo_id):
    return json(test_todo)


@todos.put("/<todo_id:int>", strict_slashes=True)
@openapi.summary("Updates a todo item")
@openapi.body(Todo, description='Todo object for update')
@openapi.response(200, Todo)
@openapi.secured(TodoApiKey)
def todo_put(request, todo_id):
    return json(test_todo)


@todos.delete("/<todo_id:int>", strict_slashes=True)
@openapi.summary("Deletes a todo")
@openapi.response(204)
@openapi.secured(TodoApiKey)
def todo_delete(request, todo_id):
    return json({})


openapi.describe('Todo API', '0.0.1', description='Advanced Todo API for own purposes')
openapi.contact('John Doe', 'https://example.com', 'info@example.com')
openapi.license('MIT')

app.blueprint(todos)
app.blueprint(openapi.blueprint)

app.run(host="0.0.0.0", debug=True)
