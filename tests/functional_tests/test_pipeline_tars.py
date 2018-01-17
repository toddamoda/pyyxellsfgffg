from pathlib import Path

import pytest

from astropy.io import fits
import numpy as np

import pyxel.pipelines.detection_pipeline
from pyxel.detectors.ccd import CCD
from pyxel.pipelines import ccd_pipeline
from pyxel.pipelines.yaml_processor import load_config
from pyxel.util.fitsfile import FitsFile

np.random.seed(19690906)


def save_signal(ccd: CCD, output_filename: Path):
    """ Save the 'signal' from a `CCDDetector` object into a FITS file.

    :param ccd:
    :param output_filename:
    """
    data = ccd.readout_signal.value         # remove the unit

    # creating new fits file with new data
    new_fits_file = FitsFile(output_filename)
    new_fits_file.save(data)

    # # writing ascii output file
    # if opts.output.data:
    #     out_file = get_data_dir(opts.output.data)
    #     with open(out_file, 'a+') as file_obj:
    #         data = [
    #             '{:6d}'.format(opts.ccd.photons),
    #             '{:8.2f}'.format(signal_mean),
    #             '{:7.2f}'.format(signal_sigma)
    #         ]
    #         out_str = '\t'.join(data) + '\n'
    #         file_obj.write(out_str)


@pytest.mark.parametrize("input_filename", [
    'pipeline_tars.yaml',
])
def test_pipeline_tars(input_filename):

    # Step 1: Get the pipeline configuration
    config_path = Path(__file__).parent.joinpath(input_filename)
    cfg = load_config(str(config_path))
    processor = cfg['process']          # type:

    # Step 2: Run the pipeline
    result = pyxel.pipelines.detection_pipeline.run_pipeline(processor.ccd, processor.pipeline)  # type: CCD
    print('Pipeline completed.')

    # Step 3: Save the result(s) in FITS, ASCII, Jupyter Notebook(s), ...
    save_signal(ccd=result, output_filename='result.fits')

    data_out = fits.getdata('result.fits')
    data_exp = fits.getdata('tests/functional_tests/expected_result.fits')

    np.testing.assert_array_equal(data_out, data_exp)

