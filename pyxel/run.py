#   --------------------------------------------------------------------------
#   Copyright 2017 SRE-F, ESA (European Space Agency)
#   --------------------------------------------------------------------------
""" PYXEL is a detector simulation framework, that can simulate a variety of
detector effects (e.g., cosmics, radiation-induced CTI  in CCDs, persistency
in MCT, diffusion, cross-talk etc.) on a given image.
"""
import logging
import argparse

from pathlib import Path

import pyxel
from pyxel.util import FitsFile
import pyxel.pipelines.processor


def run_pipeline(input_filename, output_file):

    config_path = Path(__file__).parent.joinpath(input_filename)
    cfg = pyxel.load_config(config_path)

    processor = cfg['process']

    # Step 2: Run the pipeline
    # result = pyxel.detection_pipeline.run_ccd_pipeline(processor.detector, processor.pipeline)  # type: CCD
    # result = pyxel.detection_pipeline.run_cmos_pipeline(processor.detector, processor.pipeline)  # type: CMOS

    result = processor.pipeline.run_pipeline(processor.detector)

    print('Pipeline completed.')

    if output_file:
        out = FitsFile(output_file)
        out.save(result.signal, header=None, overwrite=True)        # TODO should replace result.signal to result.image


def main():
    """ main entry point. """
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                     description=__doc__)

    parser.add_argument('-v', '--verbosity', action='count', default=0,
                        help='Increase output verbosity')
    parser.add_argument('--version', action='version',
                        version='%(prog)s (version {version})'.format(version=pyxel.__version__))

    # Required positional arguments
    parser.add_argument('-c', '--config',
                        help='Configuration file to load (YAML or INI)')

    # Required positional arguments
    parser.add_argument('-o', '--output',
                        help='output file')

    opts = parser.parse_args()

    # Set logger
    log_level = [logging.ERROR, logging.INFO, logging.DEBUG][min(opts.verbosity, 2)]
    log_format = '%(asctime)s - %(name)s - %(funcName)s - %(thread)d - %(levelname)s - %(message)s'
    logging.basicConfig(level=log_level, format=log_format)

    run_pipeline(opts.config, opts.output)


if __name__ == '__main__':
    main()
