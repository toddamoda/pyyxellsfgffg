"""Unittests for the 'Calibration' class."""

import pytest
import pygmo as pg
import esapy_config as om
from pyxel.calibration.util import read_data, list_to_slice, check_ranges


@pytest.mark.parametrize('config',
                         [
                             'tests/data/calibrate.yaml',
                             'tests/data/calibrate_sade.yaml',
                             'tests/data/calibrate_sga.yaml',
                             'tests/data/calibrate_nlopt.yaml',
                             'tests/data/calibrate_models.yaml',
                             'tests/data/calibrate_custom_fitness.yaml',
                             'tests/data/calibrate_fits.yaml',
                          ])
def test_set_algo(config):
    """Test """
    cfg = om.load(config)
    simulation = cfg['simulation']
    obj = simulation.calibration.algorithm.get_algorithm()
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


@pytest.mark.parametrize('input_data',
                         [
                             [1., 3., 2., 5.],
                             [1, 3, 2, 5],
                             [1, 10],
                             [10, 1],
                             [0, 0],
                             None,
                             # [1],              # TODO
                             # [1, 2, 3],
                             # [1, 2, 3, 4, 5],
                          ])
def test_list_to_slice(input_data):
    """Test """
    output = list_to_slice(input_data)
    if isinstance(output, slice):
        pass
    elif isinstance(output, tuple) and all(isinstance(item, slice) for item in output):
        pass
    else:
        raise TypeError
    print(output)


@pytest.mark.parametrize('target_row, range_col, row, col',
                         [

                          ])
def test_check_ranges(target_row, range_col, row, col):     # TODO
    """Test """
    # output = check_ranges(target_row, range_col, row, col)
    pass


# # @pytest.mark.parametrize('data',
# #                          [])
# def test_run_calibration():
#     """Test """
#     cfg = om.load('tests/data/calibrate_models.yaml')
#     processor = cfg['processor']
#     simulation = cfg['simulation']
#     result = simulation.calibration.run_calibration(processor)
#     assert result == 1
