from sanic import Sanic
from sanic_openapi3 import blueprint

# ------------------------------------------------------------ #
#  GET
# ------------------------------------------------------------ #


def test_get_spec():
    app = Sanic('test_get')
    app.blueprint(blueprint)

    request, response = app.test_client.get('/openapi.json')
    assert response.status == 200
