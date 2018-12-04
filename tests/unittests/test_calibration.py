"""Unittests for the 'Calibration' class."""

import pytest
import pygmo as pg
import esapy_config as om
from pyxel.calibration.calibration import Calibration
from pyxel.calibration.calibration import read_data


yaml_dict1 = {
  'calibration_mode': 'pipeline',
  'algorithm': 'sade',
  'generations': 2
}
yaml_dict2 = {
  'calibration_mode': 'pipeline',
  'algorithm': 'sga',
  'generations': 3
}
yaml_dict3 = {
  'calibration_mode': 'pipeline',
  'algorithm': 'nlopt',
  'generations': 4
}


@pytest.mark.parametrize('data',
                         [yaml_dict1,
                          yaml_dict2,
                          yaml_dict3])
def test_set_algo(data):
    """Test """
    cal = Calibration(data)
    obj = cal.set_algorithm()
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
