
import json

from copy import deepcopy as copy
from traitlets import HasTraits, Unicode, validate, TraitError

from ._util import Util


class ParamsAuth0(HasTraits):
    """
    See Auth0 doc https://auth0.com/docs/api/authentication#authorize-application
    """

    name = Unicode()
    response_type = Unicode()
    domain = Unicode()
    client_id = Unicode()
    redirect_uri = Unicode()
    audience = Unicode()
    scope = Unicode()

    def __init__(self,
                 name='auth0',
                 response_type=None,
                 domain=None,
                 client_id=None,
                 redirect_uri=None,
                 audience=None,
                 scope=None,

                 dotenv_folder='.',
                 dotenv_file=None,
                 ):
        """
        """
        dic = Util.load_dotenv(dotenv_folder,
                               dotenv_file,
                               name)

        for k, v in dic.items():
            setattr(self, k, v)

        self.name = name

        # overrides
        if response_type:
            self.response_type = response_type
        if domain:
            self.domain = domain
        if client_id:
            self.client_id = client_id
        if redirect_uri:
            self.redirect_uri = redirect_uri
        if audience:
            self.audience = audience
        if scope:
            self.scope = scope

        self.authorize_endpoint = self.build_authorize_endpoint()

        self.data = self.build_data()

    def to_dict(self):
        """
        """
        d = copy(self.__dict__)
        d = {k: v for k, v in d.items() if v is not None}
        return d

    def __repr__(self):
        """
        """
        return json.dumps(self.data, sort_keys=False, indent=2)

    @validate('response_type')
    def _valid_response_type(self, proposal):
        """
        """
        elmts = proposal['value'].split(' ')
        if not ('id_token' in elmts):
            raise TraitError('response_type must contain "id_token"')
        if not ('token' in elmts):
            raise TraitError('response_type must contain "token"')
        return proposal['value']

    @validate('redirect_uri')
    def _valid_redirect_uri(self, proposal):
        """
        """
        if not Util.is_url(proposal['value']):
            raise TraitError('redirect_uri must be a url')
        return proposal['value']

    @validate('scope')
    def _valid_scope(self, proposal):
        """
        """
        elmts = proposal['value'].split(' ')
        if not ('profile' in elmts) and not ('openid' in elmts) and not ('mail' in elmts):
            raise TraitError('scope must contain "profile" and "openid" and "mail"')
        return proposal['value']

    def build_authorize_endpoint(self):
        """
        """
        return 'https://'+self.domain+'/authorize'

    def build_data(self):
        """
        """
        props_params = ['name',
                        'authorize_endpoint',
                        ]
        props_url_params = ['response_type',
                            'client_id',
                            'redirect_uri',
                            'audience',
                            'scope',
                            ]

        data = {}
        for k in props_params:
            v = getattr(self, k)
            if v != '':
                data[k] = v

        data_url = {}
        for k in props_url_params:
            v = getattr(self, k)
            if v != '':
                data_url[k] = v

        data['url_params'] = data_url

        return data
