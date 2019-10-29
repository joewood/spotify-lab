
import json
import requests as rq

from jose import jwt

from .config import JWTKS_URL


class JWTKS:
    """
    """

    def __init__(self,
                 verbose=False):
        """
        """
        r = rq.get(JWTKS_URL)
        try:
            self.data = json.loads(r.content.decode('utf-8'))
        except:
            raise Exception('Cannot download JWT key set from {}'.format(JWTKS_URL))
        if verbose:
            print('>> JWTKS loaded')

    def decode_token_rs256(self,
                           token,
                           audience,
                           verbose=False):
        """
        See https://auth0.com/docs/jwks
        """
        header = jwt.get_unverified_header(token)
        kid = header['kid']

        match = False
        for e in self.data['keys']:
            if e['kid'] == kid:
                match = True
                key = e
                break

        if not match:
            raise Exception('Unknown sign key - Cannot decode token')

        cert = \
            '-----BEGIN CERTIFICATE-----\n' + \
            key['x5c'][0] + \
            '\n-----END CERTIFICATE-----'

        token_info = jwt.decode(token,
                                key=cert,
                                algorithms=['RS256'],
                                audience=audience)

        if verbose:
            print('>> token_info:')
            print(token_info)
        return token_info
