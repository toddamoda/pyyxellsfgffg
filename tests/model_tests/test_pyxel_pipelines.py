"""Functional tests for the Pyxel pipelines."""
import pytest
import numpy as np
from pyxel.run import run
# from pyxel.util.fitsfile import FitsFile
from astropy.io import fits


@pytest.mark.parametrize('yaml, expected_image, seed',
                         [
                             ('tests/data/pipeline_01.yaml', 'tests/data/expected_pipeline_01.fits', 1111),
                             ('tests/data/pipeline_02.yaml', 'tests/data/expected_pipeline_01.fits', 1111),
                          ])
def test_pyxel_pipeline(yaml, expected_image, seed):
    """Test """
    output = run(input_filename=yaml, output_file='tests/data/temp.fits', random_seed=seed)
    image = fits.getdata(output[0])
    expected_image = fits.getdata(expected_image)
    np.testing.assert_array_equal(image, expected_image)
