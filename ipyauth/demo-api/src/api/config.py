
TENANT_URL = 'https://ipyauth-demo.eu.auth0.com'
REDIRECT_URL = 'http://localhost:5000/api/fruit'
USER_INFO_URL = TENANT_URL + '/userinfo'
JWTKS_URL = TENANT_URL + '/.well-known/jwks.json'

AUDIENCE = 'api/fruit'

DIC_FRUIT = {'usual': ['apple', 'orange', 'cherry', 'apricot'],
             'exotic': ['kiwi', 'lychee', 'papaya', 'durian']}

