"""Unittests for the 'Calibration' class."""

import pytest
import pygmo as pg
import esapy_config as om
from pyxel.calibration.calibration import read_data


@pytest.mark.parametrize('config',
                         [
                             'tests/data/calibrate_pipeline.yaml',
                             'tests/data/calibrate_pipeline_sade.yaml',
                             'tests/data/calibrate_pipeline_sga.yaml',
                             'tests/data/calibrate_pipeline_nlopt.yaml',
                             'tests/data/calibrate_pipeline_models.yaml',
                             'tests/data/calibrate_pipeline_custom_fitness.yaml',        # todo
                             'tests/data/calibrate_pipeline_fits.yaml',
                          ])
def test_set_algo(config):
    """Test """
    cfg = om.load(config)
    simulation = cfg['simulation']
    obj = simulation.calibration.set_algorithm()
    if isinstance(obj, pg.sade):
        pass
    elif isinstance(obj, pg.sga):
        pass
    elif isinstance(obj, pg.nlopt):
        pass
    else:
        raise ReferenceError


@pytest.mark.parametrize('input_data',
                         ['tests/data/expected_ccd_pipeline01.fits',
                          'tests/data/data.npy',
                          'tests/data/cti-data.txt',
                          ['tests/data/expected_ccd_pipeline01.fits'],
                          ['tests/data/data.npy'],
                          ['tests/data/cti-data.txt']
                          ])
def test_read_data(input_data):
    """Test """
    output = read_data(input_data)
    if isinstance(output, list):
        pass
    else:
        raise TypeError
    print(output)


# @pytest.mark.parametrize('data',
#                          [])
def test_run_calibration():
    """Test """
    cfg = om.load('tests/data/calibrate_pipeline_models.yaml')
    processor = cfg['processor']
    simulation = cfg['simulation']
    result = simulation.calibration.run_calibration(processor)
    assert result == 1
