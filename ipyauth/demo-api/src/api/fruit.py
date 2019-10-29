
import requests as rq

from flask import request
from flask_restful import Resource

from .jwtks import JWTKS
from .token import Token
from .config import AUDIENCE, DIC_FRUIT


class FruitApi(Resource):
    """
    """
    jwtks = JWTKS(verbose=True)
    dic_fruit = DIC_FRUIT

    def get(self):
        """
        read fruit lists
        """

        try:
            token = request.headers['Authorization'].split(' ')[1]
        except:
            output = {'msg': 'Missing token'}
            return output, 403

        try:
            audience = AUDIENCE
            token_info = FruitApi.jwtks.decode_token_rs256(token,
                                                           audience,
                                                           verbose=True)
        except:
            output = {'msg': 'Invalid token'}
            return output, 403

        valid = Token.validate(token_info)
        if not valid:
            output = {'msg': 'Token expired'}
            return output, 403

        scopes = token_info['scope'].split(' ')

        if 'read:exotic-fruit' in scopes:
            msg = 'matched scope read:exotic-fruit'
            fruits = FruitApi.dic_fruit
            status_code = 200

        elif 'read:usual-fruit' in scopes:
            msg = 'matched scope read:usual-fruit'
            fruits = FruitApi.dic_fruit['usual']
            status_code = 200

        else:
            msg = 'No matched scope'
            fruits = None
            status_code = 403

        output = {'msg': msg,
                  'fruits': fruits,
                  'token_info': token_info}
        print(output)
        return output, status_code

    def post(self):
        """
        add to fruit lists
        """

        dic_new_fruit = request.json
        print('dic_new_fruit')
        print(dic_new_fruit)

        try:
            token = request.headers['Authorization'].split(' ')[1]
        except:
            output = {'msg': 'Missing token'}
            return output, 403

        try:
            audience = 'api/fruit'
            token_info = FruitApi.jwtks.decode_token_rs256(token, audience)
        except:
            output = {'msg': 'Invalid token'}
            return output, 403

        print(token_info)

        valid = Token.validate(token_info)
        if not valid:
            output = {'msg': 'Token expired'}
            return output, 403

        scopes = token_info['scope'].split(' ')

        if 'write:exotic-fruit' in scopes:
            msg = 'matched scope read:exotic-fruit'
            dic_new = {k: v for k, v in dic_new_fruit.items()
                       if k in FruitApi.dic_fruit}
            print(dic_new)
            dic_added = {k: [e for e in v if not e in FruitApi.dic_fruit[k]]
                         for k, v in dic_new.items()}
            for k in dic_new:
                FruitApi.dic_fruit[k] = FruitApi.dic_fruit[k] + dic_added[k]
            status_code = 200

        elif 'write:usual-fruit' in scopes:
            msg = 'matched scope read:usual-fruit'
            dic_new = {k: v for k, v in dic_new_fruit.items()
                       if k == 'usual'}
            print(dic_new)
            dic_added = {k: [e for e in v if not e in FruitApi.dic_fruit[k]]
                         for k, v in dic_new.items()}
            print(dic_new)
            print(FruitApi.dic_fruit)
            for k in dic_new:
                FruitApi.dic_fruit[k] = FruitApi.dic_fruit[k] + dic_added[k]
            print(FruitApi.dic_fruit)
            status_code = 200

        else:
            msg = 'No matched scope'
            dic_added = {}
            status_code = 403

        output = {'msg': msg,
                  'fruits_added': dic_added,
                  'token_info': token_info}
        print(output)
        return output, status_code
