
import os
import warnings
from tornado import gen
from oauthenticator.generic import LocalGenericOAuthenticator

class GitHubEnvAuthenticator(LocalGenericOAuthenticator):
    @gen.coroutine
    def pre_spawn_start(self, user, spawner):
        auth_state = yield user.get_auth_state()
        if not auth_state:
            # user has no auth state
            spawner.environment['SPOTIFY_TOKEN'] = "ERROR"
            warnings.warn("Cannot Find Auth State")
            return
        # define some environment variables from auth_state
        spawner.environment['SPOTIFY_TOKEN'] = auth_state['access_token']

if 'JUPYTERHUB_CRYPT_KEY' not in os.environ:
    warnings.warn(
        "Need JUPYTERHUB_CRYPT_KEY env for persistent auth_state.\n"
        "    export JUPYTERHUB_CRYPT_KEY=$(openssl rand -hex 32)"
    )
    c.CryptKeeper.keys = [ "8f81b238944881062ce2aaf98b7137ff3ab9ffaa411471222a75eebde7389c34" ]

def userMap( x):
    return "jovyan"

c.JupyterHub.authenticator_class = GitHubEnvAuthenticator
c.GenericOAuthenticator.enable_auth_state = True
c.GenericOAuthenticator.authorize_url = "https://accounts.spotify.com/authorize"
c.GenericOAuthenticator.client_secret = os.environ["OAUTH_CLIENT_SECRET"]
c.GenericOAuthenticator.client_id = os.environ["OAUTH_CLIENT_ID"]
c.GenericOAuthenticator.oauth_callback_url = "http://localhost:8000/hub/oauth_callback" 
c.GenericOAuthenticator.userdata_url = "https://api.spotify.com/v1/me" 
c.GenericOAuthenticator.username_key = userMap
c.GenericOAuthenticator.refresh_pre_spawn = True
c.GenericOAuthenticator.tls_verify = False
c.GenericOAuthenticator.auto_login = True
c.GenericOAuthenticator.scope = ["user-read-private", "user-read-email", "playlist-modify-public", "playlist-modify-private", "user-library-read", "user-library-read", "user-library-modify", "playlist-read-private", "playlist-read-collaborative"]
c.GenericOAuthenticator.token_url = "https://accounts.spotify.com/api/token"

