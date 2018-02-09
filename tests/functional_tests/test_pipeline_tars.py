from pathlib import Path

import pytest

from astropy.io import fits
import numpy as np

from pyxel.pipelines import detection_pipeline
from pyxel.detectors.ccd import CCD
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


@pytest.mark.parametrize("input_filename, exp_filename", [
    ('tests/data/pipeline_tars.yaml', 'tests/data/expected_ccd_pipeline01.fits'),
])
def test_pipeline_tars(input_filename, exp_filename):

    # Step 1: Get the pipeline configuration
    cfg = load_config(Path(input_filename))
    processor = cfg['process']  # type: detection_pipeline.Processor

    pipeline = processor.pipeline  # type: t.Union[CCDDetectionPipeline, CMOSDetectionPipeline]

    # Step 2: Run the pipeline
    result = pipeline.run_pipeline(processor.detector)  # type: CCD
    print('Pipeline completed.')

    expected = fits.getdata(exp_filename)
    image = result.image  # type: np.ndarray

    assert isinstance(image, np.ndarray)
    np.testing.assert_array_equal(image, expected)

    # save_signal(ccd=result, output_filename='result')
