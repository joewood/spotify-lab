
import os
from notebook.base.handlers import IPythonHandler
from notebook.utils import url_path_join


def load_jupyter_server_extension(nb_app):
    web_app = nb_app.web_app

    web_app.settings['jinja2_env'].loader.searchpath += [
        os.path.join(os.path.dirname(__file__), 'templates'),
        os.path.join(os.path.dirname(__file__), 'templates', 'assets'),
    ]

    class CallbackHandler(IPythonHandler):
        """
        """

        def get(self, path):
            """
            """
            nb_app.log.info('in CallbackHandler with path={}'.format(path))
            self.write(self.render_template('index.html'))

    class CallbackAssetsHandler(IPythonHandler):
        """
        """

        def prepare(self):
            self.set_header('Content-Type', 'text/javascript')

        def get(self, path):
            """
            """
            nb_app.log.info("in CallbackAssetsHandler with path={}".format(path))
            self.write(self.render_template(path))

    host_pattern = '.*$'
    base_url = web_app.settings['base_url']

    web_app.add_handlers(
        host_pattern,
        [(url_path_join(base_url, '/callback/assets/(.*)'), CallbackAssetsHandler),
         (url_path_join(base_url, '/assets/(.*)'), CallbackAssetsHandler),
         (url_path_join(base_url, '/callback(.*)'), CallbackHandler),
         (url_path_join(base_url, '/callback.html(.*)'), CallbackHandler),
         ]
    )

    nb_app.log.info("ipyauth callback server extension enabled")
