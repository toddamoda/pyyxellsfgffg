"""TBW."""

import logging
import argparse
from pathlib import Path
import typing as t  # noqa: F401

import tornado.web

from esapy_web.webapp2 import webapp
from esapy_web.webapp2 import signals

import pyxel
import pyxel.pipelines.processor

from pyxel.web2 import controller


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
    ctrl = controller.Controller()

    handlers = [
        ('/pipeline/(.*)', PipelinePageHandler, {}, None),
        ('/pyxel/(.*)', webapp.MultiStaticPage, {}, None),
        ('/js9/(.*)', tornado.web.StaticFileHandler, {'path': js9_dir}, None),
        ('/data/(.*)', tornado.web.StaticFileHandler, {'path': data_dir}, 'data'),
        # Rule(matcher, target, target_kwargs, name)
    ]   # type: t.List[t.Tuple[str, t.Any, t.Dict[str, t.Any], str]]

    settings = {
        'web_dir': str(Path(__file__).parent.joinpath('static')),
        'index_template': 'main.html',
    }
    api = webapp.WebApplication(ctrl, signals.dispatcher, handlers, settings)

    def set_data_path(path, *args):
        web_uri = path.split('data')[0] + 'data'
        api.wildcard_router.named_rules['data'].target_kwargs['path'] = web_uri

    signals.dispatcher.connect(sender='api', signal=controller.OUTPUT_DATA_DIR, callback=set_data_path)
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

    parser.add_argument('-d', '--data-dir', default='../data',
                        help='Data directory')

    parser.add_argument('-j', '--js9-dir', default='../pyxel_js9',
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
