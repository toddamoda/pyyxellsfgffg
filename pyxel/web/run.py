"""TBW."""

import logging
import argparse

from pathlib import Path

import pyxel
import pyxel.pipelines.processor

from pyxel.web import webapp
from pyxel.web.controller import API


def run_web_server(input_filename, port=8888):
    """TBW.

    :param input_filename:
    :param port:
    :return:
    """
    config_path = Path(__file__).parent.parent.joinpath(input_filename)
    cfg = pyxel.load_config(config_path)
    processor = cfg['process']

    controller = API(processor)

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

    parser.add_argument('-v', '--verbosity', action='count', default=0,
                        help='Increase output verbosity')
    parser.add_argument('--version', action='version',
                        version='%(prog)s (version {version})'.format(version=pyxel.__version__))

    # Required positional arguments
    parser.add_argument('-c', '--config',
                        help='Configuration file to load (YAML or INI)')

    # # Required positional arguments
    # parser.add_argument('-o', '--output',
    #                     help='output file')

    opts = parser.parse_args()

    # Set logger
    log_level = [logging.ERROR, logging.INFO, logging.DEBUG][min(opts.verbosity, 2)]
    log_format = '%(asctime)s - %(name)s - %(funcName)s - %(thread)d - %(levelname)s - %(message)s'
    del logging.root.handlers[:]
    logging.basicConfig(level=log_level, format=log_format)

    run_web_server(opts.config)


if __name__ == '__main__':
    main()
