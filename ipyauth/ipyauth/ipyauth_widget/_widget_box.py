
import string

import random as rd
import ipywidgets as wg

from traitlets import HasTraits, Unicode, Dict, Int

from ..__meta__ import __version_js__
from ._config import DIC_LOGO



_semver_range_frontend_ = '~' + __version_js__


class Auth(wg.VBox):
    """
    Auth widget made of ipywidgets
    """
    _model_name = Unicode('AuthModel').tag(sync=True)
    _view_name = Unicode('AuthView').tag(sync=True)
    _model_module = Unicode('ipyauth').tag(sync=True)
    _view_module = Unicode('ipyauth').tag(sync=True)
    _model_module_version = Unicode(_semver_range_frontend_).tag(sync=True)
    _view_module_version = Unicode(_semver_range_frontend_).tag(sync=True)

    name = Unicode('').tag(sync=True)
    _id = Unicode('').tag(sync=True)

    params = Dict({}).tag(sync=True)

    access_token = Unicode('').tag(sync=True)
    code = Unicode('').tag(sync=True)
    scope = Unicode('').tag(sync=True)
    logged_as = Unicode('').tag(sync=True)
    time_to_exp = Unicode('').tag(sync=True)
    expires_at = Unicode('').tag(sync=True)

    _incr_signout = Int(0).tag(sync=True)

    def __init__(self,
                 params=None):
        """
        """
        msg = 'params must be a Params[IdProvider] object'
        test1 = issubclass(params.__class__, HasTraits)
        cname = str(params.__class__)
        test2 = 'ipyauth.ipyauth_widget._params_' in cname and '.Params' in cname
        assert test1 and test2, msg

        # dic = {}
        uuid = ''.join([rd.choice(string.ascii_lowercase) for n in range(6)])

        self.params = params.data
        self.name = self.params['name']
        self._id = self.name + '-' + uuid

        wg_logo = self.build_widget_logo()
        wg_button_main = self.build_widget_button_main()
        wg_logged_as = self.build_widget_logged_as()
        wg_time_to_exp = self.build_widget_time_to_exp()
        wg_expire_at = self.build_widget_expire_at()
        wg_button_inspect = self.build_widget_button_inspect()
        wg_scope = self.build_widget_scope()

        b1 = wg.HBox([wg_logo,
                      wg_button_main,
                      wg_logged_as,
                      wg_time_to_exp,
                      wg_expire_at,
                      wg_button_inspect,
                      ]
                     )
        b2 = wg.HBox([wg_scope])

        super().__init__([b1, b2])

    def build_widget_logo(self):
        """
        """
        path_img = DIC_LOGO[self.name]
        with open(path_img, 'rb') as f:
            image = f.read()

        widget = wg.Image(
            value=image,
            format='png',
            layout=wg.Layout(
                max_height='26px',
                margin='3px',
                align_self='center'),
        )
        return widget

    def build_widget_button_main(self):
        """
        """
        widget = wg.Button(
            description='Sign In',
            button_style='info',
            layout=wg.Layout(width='90px',
                             margin='0 5px 0 5px',
                             align_self='center'),
        )
        widget.style.button_color = '#4885ed'
        return widget

    def build_widget_button_inspect(self):
        """
        """
        widget = wg.Button(
            description='Inspect',
            button_style='',
            layout=wg.Layout(width='90px',
                             margin='0 0 0 5px',
                             align_self='center'),
        )
        return widget

    def build_widget_logged_as(self):
        """
        """
        widget = wg.HTML(
            layout=wg.Layout(
                width='275px',
                border='1px lightgray solid',
                padding='3px',
                overflow_x='auto')
        )
        return widget

    def build_widget_time_to_exp(self):
        """
        """
        widget = wg.HTML(
            layout=wg.Layout(
                width='70px',
                border='1px lightgray solid',
                padding='3px')
        )
        return widget

    def build_widget_expire_at(self):
        """
        """
        widget = wg.HTML(
            layout=wg.Layout(
                width='300px',
                # max_height='28px',
                border='1px lightgray solid',
                padding='3px')
        )
        return widget

    def build_widget_scope(self):
        """
        """
        widget = wg.HTML(
            layout=wg.Layout(
                overflow_y='scroll',
                border='1px lightgray solid ',
                width='827px',
                height='47px',
                margin='5px 0 0 5px'
            )
        )
        return widget

    def show(self):
        """
        """
        for attr in ['name',
                     '_id',
                     'params',
                     'logged_as',
                     'time_to_exp',
                     'expires_at',
                     'scope',
                     'access_token',
                     '_incr_signout',
                     ]:
            print('{} = {}'.format(attr, getattr(self, attr)))

    def clear(self):
        """
        """
        self._incr_signout += 1
