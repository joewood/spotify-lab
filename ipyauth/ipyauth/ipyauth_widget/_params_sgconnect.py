
import json

from copy import deepcopy as copy
from traitlets import HasTraits, Unicode, validate, TraitError

from ._util import Util


class ParamsSgConnect(HasTraits):
    """
    """

    name = Unicode()
    response_type = Unicode()
    domain = Unicode()
    client_id = Unicode()
    redirect_uri = Unicode()
    audience = Unicode()
    scope = Unicode()

    def __init__(self,
                 mode='PRD', # PRD or HOM
                 response_type=None,
                 client_id=None,
                 redirect_uri=None,
                 scope=None,

                 dotenv_folder='.',
                 dotenv_file=None,
                 ):
        """
        """
        name = 'sgconnect' + mode

        dic = Util.load_dotenv(dotenv_folder,
                               dotenv_file,
                               name)

        for k, v in dic.items():
            setattr(self, k, v)

        self.name = name

        # overrides
        if response_type:
            self.response_type = response_type
        if client_id:
            self.client_id = client_id
        if redirect_uri:
            self.redirect_uri = redirect_uri

        self.scope = self.build_scope(scope)
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

    @validate('name')
    def _valid_response_type(self, proposal):
        """
        """
        if not (proposal == 'sgconnectPRD' or proposal == 'sgconnectHOM'):
            raise TraitError('mode must be "PRD" (default) or "HOM" (aka UAT)')
        return proposal['value']

    @validate('response_type')
    def _valid_response_type(self, proposal):
        """
        """
        elmts = proposal['value'].split(' ')
        if not 'id_token' in elmts:
            raise TraitError('response_type must be contain "id_token"')
        if not 'token' in elmts:
            raise TraitError('response_type must be contain "token"')
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
        if not ('profile' in elmts) and not ('openid' in elmts):
            raise TraitError('scope must contain "profile" and "openid" and "mail"')
        return proposal['value']

    def build_scope(self, scope):
        """
        """
        scopes = [e.strip() for e in scope.split(' ')] + ['openid', 'profile']
        return ' '.join(list(set(scopes)))

    def build_data(self):
        """
        """
        props_params = ['name',
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
