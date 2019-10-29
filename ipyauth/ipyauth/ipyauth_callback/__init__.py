
from ..__meta__ import __version__

def _jupyter_server_extension_paths():
    # path to file containing function load_jupyter_server_extension
    return [{'module': 'ipyauth.ipyauth_callback.server_extension'}]
