import json
from copy import deepcopy as copy
from traitlets import HasTraits, Unicode, validate, TraitError
from ._util import Util


class ParamsSpotify(HasTraits):
    name = Unicode()
    response_type = Unicode()
    authorize_endpoint = Unicode()
    client_id = Unicode()
    redirect_uri = Unicode()
    scope = Unicode()
    include_granted_scopes = Unicode()
    access_type = Unicode()

    def __init__(self,
                 name='spotify',
                 response_type=None,
                 client_id=None,
                 redirect_uri=None,
                 scope="user-read-private user-read-email playlist-modify-public playlist-modify-private user-library-read user-library-read user-library-modify playlist-read-private playlist-read-collaborative",
                 ):
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

        self.data = self.build_data()

    def to_dict(self):
        d = copy(self.__dict__)
        d = {k: v for k, v in d.items() if v is not None}
        return d

    def __repr__(self):
        return json.dumps(self.data, sort_keys=False, indent=2)

    @validate('response_type')
    def _valid_response_type(self, proposal):
        return proposal['value']

    @validate('redirect_uri')
    def _valid_redirect_uri(self, proposal):
     #   if not Util.is_url(proposal['value']):
     #       raise TraitError('redirect_uri must be an https url')
        return proposal['value']

    @validate('scope')
    def _valid_scope(self, proposal):
        return proposal['value']

    def build_data(self):
        props_params = ['name']
        props_url_params = ['response_type',
                            'client_id',
                            'redirect_uri',
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
