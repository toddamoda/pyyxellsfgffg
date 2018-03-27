"""TBW."""

import logging
import argparse
from pathlib import Path
import tornado.web

from esapy_web.webapp2 import webapp
from esapy_web.webapp2 import signals

import pyxel
import pyxel.pipelines.processor

from pyxel.web2.controller import Controller


class PipelinePageHandler(webapp.IndexPageHandler):
    """The index.html HTML generation handler."""

    def get(self, name):
        """TBW."""
        self.application.controller.load_template(name)
        super(PipelinePageHandler, self).get()


def run_web_server(port=9999, js9_dir=None, data_dir=None):
    """TBW.

    :param port:
    :param js9_dir:
    :param data_dir:
    """
    controller = Controller()

    handlers = [
        ('/pyxel/(.*)', webapp.MultiStaticPage),
        (r'/pipeline/(.*)', PipelinePageHandler),
    ]
    web_dir = str(Path(__file__).parent.joinpath('static'))
    settings = {
        'web_dir': web_dir,
        'index_template': 'main.html',
    }
    api = webapp.WebApplication(controller, signals.dispatcher, handlers, settings)

    thread = webapp.TornadoServer(api, ('0.0.0.0', port))
    try:
        thread.run()
    except KeyboardInterrupt:
        logging.info("Exiting web server")
    finally:
        thread.stop()


def main():
    """TBW."""
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                     description=__doc__)

    parser.add_argument('-p', '--port', default=9999, type=int,
                        help='The port to run the web server on')

    parser.add_argument('-d', '--data-dir',
                        help='Data directory')

    parser.add_argument('-j', '--js9-dir',
                        help='JS9 directory')

    parser.add_argument('-v', '--verbosity', action='count', default=0,
                        help='Increase output verbosity')

    parser.add_argument('--version', action='version',
                        version='%(prog)s (version {version})'.format(version=pyxel.__version__))

    opts = parser.parse_args()

    # Set logger
    log_level = [logging.ERROR, logging.INFO, logging.DEBUG][min(opts.verbosity, 2)]
    log_format = '%(asctime)s - %(levelname)s - %(name)s - %(funcName)s - %(thread)d - %(message)s'
    del logging.root.handlers[:]
    logging.basicConfig(level=log_level, format=log_format)

    run_web_server(opts.port, opts.js9_dir, opts.data_dir)


if __name__ == '__main__':
    main()
