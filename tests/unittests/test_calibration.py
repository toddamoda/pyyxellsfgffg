"""Unittests for the 'Calibration' class."""

import pytest
import pygmo as pg
import esapy_config.io as io
from pyxel.calibration.util import read_data, list_to_slice, check_ranges
from pyxel.pipelines.processor import Processor


@pytest.mark.parametrize('yaml',
                         [
                             'tests/data/calibrate.yaml',
                             'tests/data/calibrate_sade.yaml',
                             'tests/data/calibrate_sga.yaml',
                             'tests/data/calibrate_nlopt.yaml',
                             'tests/data/calibrate_models.yaml',
                             'tests/data/calibrate_custom_fitness.yaml',
                             'tests/data/calibrate_fits.yaml',
                          ])
def test_set_algo(yaml):
    """Test """
    cfg = io.load(yaml)
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


@pytest.mark.parametrize('targ_range, out_range, row, col',
                         [
                             ([0, 2, 0, 2], [0, 2, 0, 2], 5, None),
                             ([0, 3, 0, 2], [0, 2, 0, 2], 5, 5),
                             ([0, 2, 0, 2], [0, 2, 0, 3], 5, 5),
                             ([0, 2, 0, 2], [0, 2, 0, 2], 1, 5),
                             ([0, 2, 0, 2], [0, 2, 0, 2], 1, 1),
                             ([0, 2, 0, 2], [0, 2, 0, 2], 0, 0),
                             ([0, 2], [0, 3], 3, 3),
                             ([-1, 2], [0, 2], 3, 3),
                             ([-1, 1], [0, 2], 3, 3),
                             ([0, 2], [0, 2], 1, 1),
                             ([0, 2], [0, 2], 0, 0),
                             ([0, 2], [0, 2], 0, None),
                             ([0, 2], [0, 2], 0, 0),
                             ([0], [0, 2], 4, 4),
                             ([0, 2], [0, 2, 3], 4, 4),
                             ([0, 2, 0, 4], [0, 2, 0, 4], 3, 3),
                             ([0, 2, -2, 2], [0, 2, -2, 2], 3, 3),

                          ])
def test_check_ranges(targ_range, out_range, row, col):
    """Test """
    with pytest.raises(ValueError):
        check_ranges(targ_range, out_range, row, col)


@pytest.mark.parametrize('yaml',
                         [
                             'tests/data/calibrate_models.yaml'
                         ])
def test_run_calibration(yaml):
    """Test """
    cfg = io.load(yaml)
    detector = cfg['detector']
    pipeline = cfg['pipeline']
    processor = Processor(detector, pipeline)
    simulation = cfg['simulation']
    result = simulation.calibration.run_calibration(processor)
    assert result == 1

