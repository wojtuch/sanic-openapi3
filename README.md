# Sanic OpenAPI v3

[![Build Status](https://travis-ci.org/zloyuser/sanic-openapi3.svg?branch=master)](https://travis-ci.org/zloyuser/sanic-openapi3)
[![PyPI](https://img.shields.io/pypi/v/sanic-openapi3.svg)](https://pypi.python.org/pypi/sanic-openapi3/)
[![PyPI](https://img.shields.io/pypi/pyversions/sanic-openapi3.svg)](https://pypi.python.org/pypi/sanic-openapi3/)

Give your Sanic API an OpenAPI v3 specification.
Based on original [Sanic OpenAPI](https://github.com/channelcat/sanic-openapi) extension.

## Installation

```shell
pip install sanic-openapi3
```

## Usage

### Import blueprint and use simple decorators to document routes:

```python
from sanic import Sanic
from sanic_openapi3 import openapi

app = Sanic()

openapi.describe('Car API', '1.0.1', description='Advanced Todo API for own purposes')
openapi.contact('John Doe', 'https://example.com', 'info@example.com')
openapi.license('MIT')


@app.get("/user/<user_id:int>")
@openapi.summary("Fetches a user by ID")
@openapi.response(200, { "user": { "name": str, "id": int } })
async def get_user(request, user_id):
    ...


@app.post("/user")
@openapi.summary("Creates a user")
@openapi.body({"user": { "name": str }})
async def create_user(request):
    ...


app.blueprint(openapi.blueprint)
```

You'll now have a specification at the URL `/openapi.json`.
Your routes will be automatically categorized by their blueprints.

### Model your input/output

```python
...

from sanic_openapi3 import openapi
from sanic.response import json


class Car:
    make = str
    model = str
    year = int


class Garage:
    spaces = int
    cars = [Car]


@app.get("/garage")
@openapi.summary("Gets the whole garage")
@openapi.response(200, Garage)
async def get_garage(request):
    return json({
        "spaces": 2,
        "cars": [{"make": "Nissan", "model": "370Z"}]
    })

```

### Get more descriptive

```python
from openapitools.types import *


class Car:
    make = String(description="Who made the car")
    model = String(description="Type of car.  This will vary by make")
    year = Integer(description="4-digit year of the car", required=False)


class Garage:
    spaces = Integer(description="How many cars can fit in the garage")
    cars = Array(Car, description="All cars in the garage")
```

