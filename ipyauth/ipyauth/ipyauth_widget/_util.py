
import os
from dotenv.main import dotenv_values

from ._config import VALID_ID_PROVIDERS


class Util:
    """
    """

    def __init__(self):
        """
        """
        pass

    @staticmethod
    def is_url(string):
        """
        """
        return string.startswith('http')

    @staticmethod
    def load_dotenv(dotenv_folder,
                    dotenv_file,
                    prefix='IdP',
                    suffix='.env'):
        """
        """
        if dotenv_file is None:
            return {}

        msg = 'prefix must be a string in {}'.format(VALID_ID_PROVIDERS)
        assert prefix in VALID_ID_PROVIDERS, msg

        val = 'ipyauth-' + prefix + '-'
        msg = 'dotenv_file must start with ' + val
        assert dotenv_file.startswith(val), msg

        suffix = '.env'
        msg = 'dotenv_file must end with ' + suffix
        assert dotenv_file.endswith(suffix), msg

        path_dotenv = os.path.join(dotenv_folder,
                                   dotenv_file)
        msg = 'file {} does not exist'.format(path_dotenv)
        assert os.path.exists(path_dotenv), msg

        dic = dict(dotenv_values(path_dotenv))

        return dic
