from flask import Flask
from flask_restful import Api

app = Flask(__name__)
app.config['DEBUG'] = True

# create api
_api = Api(app)

# api endpoints
from .api.fruit import FruitApi
_api.add_resource(FruitApi, '/api/fruit', methods=['GET', 'POST'], endpoint='fruit')

