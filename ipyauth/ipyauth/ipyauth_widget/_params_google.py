
import json

from copy import deepcopy as copy
from traitlets import HasTraits, Unicode, validate, TraitError

from ._util import Util


class ParamsGoogle(HasTraits):
    """
    See Google doc https://developers.google.com/identity/protocols/OAuth2
    """

    name = Unicode()
    response_type = Unicode()
    authorize_endpoint = Unicode()
    client_id = Unicode()
    redirect_uri = Unicode()
    scope = Unicode()
    include_granted_scopes = Unicode()
    access_type = Unicode()

    def __init__(self,
                 name='google',
                 response_type=None,
                 client_id=None,
                 redirect_uri=None,
                 scope=None,
                 include_granted_scopes='false',

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
        if client_id:
            self.client_id = client_id
        if redirect_uri:
            self.redirect_uri = redirect_uri
        if scope:
            self.scope = scope
        if include_granted_scopes:
            self.include_granted_scopes = include_granted_scopes

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
        if not proposal['value'] == 'token':
            raise TraitError('response_type must be "token"')
        return proposal['value']

    @validate('redirect_uri')
    def _valid_redirect_uri(self, proposal):
        """
        """
        if not Util.is_url(proposal['value']):
            raise TraitError('redirect_uri must be an https url')
        return proposal['value']

    @validate('scope')
    def _valid_scope(self, proposal):
        """
        """
        elmts = proposal['value'].split(' ')
        if not ('profile' in elmts) and not ('openid' in elmts):
            raise TraitError('scope must contain "profile" and "openid"')
        return proposal['value']

    @validate('include_granted_scopes')
    def _valid_include_granted_scopes(self, proposal):
        """
        """
        if proposal['value'] not in ['true', 'false']:
            raise TraitError('include_granted_scopes must be "true" or "false"')
        return proposal['value']

    @validate('access_type')
    def _valid_access_type(self, proposal):
        """
        """
        if proposal['value'] not in ['online', 'offline']:
            raise TraitError('access_type must be "online" or "offline"')
        return proposal['value']

    def build_data(self):
        """
        """
        props_params = ['name',
                        ]
        props_url_params = ['response_type',
                            'client_id',
                            'redirect_uri',
                            'scope',
                            'include_granted_scopes',
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
