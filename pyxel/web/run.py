"""TBW."""

import logging
import argparse

from pathlib import Path

import pyxel
import pyxel.pipelines.processor

from pyxel.web import webapp
from pyxel.web.controller import API


def run_web_server(input_filename=None, port=9999, address_viewer=None):
    """TBW.

    :param input_filename:
    :param port:
    :param address_viewer:
    """
    processor = None
    if input_filename:
        config_path = Path(__file__).parent.parent.joinpath(input_filename)
        cfg = pyxel.load_config(config_path)
        processor = cfg[cfg.keys()[0]]

    controller = API(processor, address_viewer)

    api = webapp.WebApplication(controller)
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

    parser.add_argument('-a', '--address-viewer', default=None, type=str,
                        help='The remote viewer "<host>:<port>" address')

    parser.add_argument('-c', '--config',
                        help='Configuration file to load (YAML or INI)')

    parser.add_argument('-v', '--verbosity', action='count', default=0,
                        help='Increase output verbosity')

    parser.add_argument('--version', action='version',
                        version='%(prog)s (version {version})'.format(version=pyxel.__version__))

    opts = parser.parse_args()

    # Set logger
    log_level = [logging.ERROR, logging.INFO, logging.DEBUG][min(opts.verbosity, 2)]
    log_format = '%(asctime)s - %(name)s - %(funcName)s - %(thread)d - %(levelname)s - %(message)s'
    del logging.root.handlers[:]
    logging.basicConfig(level=log_level, format=log_format)

    run_web_server(opts.config, opts.port, opts.address_viewer)


if __name__ == '__main__':
    main()
