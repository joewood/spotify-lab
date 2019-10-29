
import os


def _build_dics():
    """
    """
    dic_filename = {
        'auth0': {'logo': 'auth0-logo.png'},
        'google': {'logo': 'google-logo.png'},
        'spotify': {'logo': 'spotify-logo.png'},
        'sgconnectPRD': {'logo': 'sg-logo.png'},
        'sgconnectHOM': {'logo': 'sg-logo.png'},
    }
    dic_logo = {k: os.path.join(os.path.dirname(__file__), 'img', v['logo'])
                for k, v in dic_filename.items()}
    return dic_logo


DIC_LOGO = _build_dics()
VALID_ID_PROVIDERS = list(DIC_LOGO.keys())
