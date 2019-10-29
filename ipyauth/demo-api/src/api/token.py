
import datetime as dt


class Token:
    """
    """

    def __init__(self):
        """
        """
        pass

    @staticmethod
    def validate(token_info,
                 leeway=15,
                 verbose=False):
        """
        """
        iat = token_info['iat']
        iat_dt = dt.datetime.utcfromtimestamp(token_info['iat'])

        exp = token_info['exp']
        exp_dt = dt.datetime.utcfromtimestamp(token_info['exp'])

        now_dt = dt.datetime.utcnow()
        now = dt.datetime.timestamp(now_dt)

        if verbose:
            print('\niat = {}'.format(iat_dt))
            print('\nexp = {}'.format(exp_dt))
            print('\nnow = {}'.format(now_dt))

        if now + leeway < exp:
            return True

        return False
