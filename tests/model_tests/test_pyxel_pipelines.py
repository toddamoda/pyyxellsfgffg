"""Functional tests for the Pyxel pipelines."""
import pytest
import numpy as np
from astropy.io import fits
from pyxel.run import run


@pytest.mark.parametrize('yaml, expected_image, seed',
                         [
                             ('tests/data/photon_transfer_function.yaml', 'tests/data/uniform_1000.fits', 1111),
                             ('tests/data/pipeline_01.yaml', 'tests/data/expected_pipeline_01.fits', 1111),
                             ('tests/data/pipeline_02.yaml', 'tests/data/expected_pipeline_01.fits', 1111),
                         ])
def test_pyxel_pipeline(yaml, expected_image, seed):
    """Test """
    out = 'tests/data/temp.fits'
    run(input_filename=yaml, output_file=out, random_seed=seed)
    image = fits.getdata(out)
    expected_image = fits.getdata(expected_image)
    np.testing.assert_array_equal(image, expected_image)
