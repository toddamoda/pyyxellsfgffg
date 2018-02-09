from pathlib import Path

import pytest

from astropy.io import fits
import numpy as np

# from pyxel.pipelines import detection_pipeline
# from pyxel.detectors.ccd import CCD
from pyxel.pipelines.yaml_processor import load_config

np.random.seed(19690906)


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
