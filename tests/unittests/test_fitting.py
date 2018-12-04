"""Unittests for the 'ModelFitting' class."""

import pytest
import numpy as np
import esapy_config as om
from pyxel.calibration.calibration import read_data
from pyxel.calibration.fitting import ModelFitting
from pyxel.detectors.detector import Detector
from pyxel.pipelines.detector_pipeline import DetectionPipeline


def configure(mf, sim, target=None):
    """TBW."""
    if target is None:
        target = read_data(sim.calibration.args['target_data_path'])
    population_size = 10
    sort_var = None
    mf.set_parameters(calibration_mode=sim.calibration.mode,
                      model_names=sim.calibration.args['model_names'],
                      variables=sim.calibration.args['variables'],
                      var_log=sim.calibration.args['var_log'],
                      generations=sim.calibration.generations,
                      population_size=population_size,
                      fitness_mode=sim.calibration.args['fitness_mode'],
                      simulation_output=sim.calibration.args['output'],
                      sort_by_var=sort_var)
    mf.configure(params_per_variable=sim.calibration.args['params_per_variable'],
                 target_output_list=target,
                 target_fit_range=sim.calibration.args['target_fit_range'],
                 out_fit_range=sim.calibration.args['output_fit_range'])


@pytest.mark.parametrize('yaml_file',
                         [
                             'tests/data/calibrate_pipeline.yaml',
                          ])
def test_configure_params(yaml_file):
    """Test """
    cfg = om.load(yaml_file)
    processor = cfg['processor']
    simulation = cfg['simulation']
    mf = ModelFitting(processor)

    if not isinstance(mf.pipe, DetectionPipeline):
        raise ValueError
    if not isinstance(mf.det, Detector):
        raise ValueError

    target_output = [[1., 2., 3., 4., 5., 6., 7., 8.]]
    configure(mf, simulation, target_output)

    assert mf.is_var_array == [[0], [1, 1, 0], [0]]
    assert mf.is_var_log == [[False], [True, True, False], [False]]
    assert mf.model_name_list == ['characteristics', 'cdm', 'output_node_noise']
    assert mf.params_per_variable == [[1], [2, 2, 1], [1]]
    assert mf.variable_name_lst == [['amp'], ['tr_p', 'nt_p', 'beta_p'], ['std_deviation']]
    assert mf.calibration_mode == 'pipeline'
    assert mf.fitness_mode == 'residuals'
    assert mf.sim_fit_range == slice(2, 5, None)
    assert mf.targ_fit_range == slice(1, 4, None)
    assert mf.sim_output == 'image'
    assert mf.target_data == [2., 3., 4.]
    assert mf.all_target_data == [[2., 3., 4.]]


@pytest.mark.parametrize('yaml_file',
                         [
                             'tests/data/calibrate_pipeline_fits.yaml',
                          ])
def test_configure_fits_target(yaml_file):
    """Test """
    cfg = om.load(yaml_file)
    processor = cfg['processor']
    simulation = cfg['simulation']
    mf = ModelFitting(processor)

    configure(mf, simulation)

    assert mf.sim_fit_range == (slice(2, 5, None), slice(4, 7, None))
    assert mf.targ_fit_range == (slice(1, 4, None), slice(5, 8, None))
    assert mf.sim_output == 'image'
    expected = np.array([[1362., 1378., 1411.],
                         [1308., 1309., 1284.],
                         [1390., 1346., 1218.]])
    np.testing.assert_array_equal(mf.target_data, expected)


@pytest.mark.parametrize('yaml_file',
                         [
                             'tests/data/calibrate_pipeline.yaml',
                             'tests/data/calibrate_pipeline_fits.yaml',
                          ])
def test_boundaries(yaml_file):
    """Test """
    cfg = om.load(yaml_file)
    processor = cfg['processor']
    simulation = cfg['simulation']
    mf = ModelFitting(processor)

    configure(mf, simulation)
    mf.set_bound(low_val=simulation.calibration.args['lower_boundary'],
                 up_val=simulation.calibration.args['upper_boundary'])
    lbd_expected = [1.0, -3.0, -3.0, -2.0, -2.0, 0.0, 10.0]
    ubd_expected = [10.0, 0.3010299956639812, 0.3010299956639812, 1.0, 1.0, 1.0, 200.0]
    assert mf.lbd == lbd_expected
    assert mf.ubd == ubd_expected
    l, u = mf.get_bounds()
    assert l == lbd_expected
    assert u == ubd_expected


@pytest.mark.parametrize('wf',
                         [

                          ])
def test_weighting_func(wf):
    """Test"""
    pass


@pytest.mark.parametrize('simulated_data, target_data, expected_fitness',
                         [
                             (231, 231, (0, 0)),
                             (231, 145, (86, 7396)),
                             (2.31, 1.45, (0.8600000000000001, 0.7396000000000001)),
                             (2., 1, (1.0, 1.0)),
                             (np.array([1, 9, 45, 548, 2, 2]), np.array([1, 9, 45, 548, 2, 2]), (0, 0)),
                             (np.array([1, 9, 45, 548, 2, 2]), np.array([1, 3, 56, 21, 235, 11]), (786, 332256)),
                             (np.array([[1362., 1378.], [1308., 1309.]]),
                              np.array([[1362., 1378.], [1308., 1309.]]), (0, 0)),
                             (np.array([[1362., 1378.],
                                        [1308., 1309.]]),
                              np.array([[1462., 1368.],
                                        [1508., 1399.]]), (400.0, 58200.0))
                          ])
def test_calculate_fitness(simulated_data, target_data, expected_fitness):
    """Test"""
    cfg = om.load('tests/data/calibrate_pipeline.yaml')
    processor = cfg['processor']
    simulation = cfg['simulation']
    mf = ModelFitting(processor)
    configure(mf, simulation)
    mf.fitness_mode = 'residuals'
    fitness = mf.calculate_fitness(simulated_data, target_data)
    assert fitness == expected_fitness[0]
    print('fitness: ', fitness)
    mf.fitness_mode = 'least-squares'
    fitness = mf.calculate_fitness(simulated_data, target_data)
    assert fitness == expected_fitness[1]
    print('fitness: ', fitness)


def custom_fitness_func(sim, targ):
    """Custom fitness func for testing"""
    return np.sum(targ * 2 - sim / 2 + 1.)


@pytest.mark.parametrize('simulated_data, target_data, expected_fitness',
                         [
                             (1., 2., 4.5),
                             (np.array([1., 2., 3.]), np.array([2., 5., 6.]), 26.),
                          ])
def test_custom_fitness(simulated_data, target_data, expected_fitness):
    """Test"""
    cfg = om.load('tests/data/calibrate_pipeline_custom_fitness.yaml')
    processor = cfg['processor']
    simulation = cfg['simulation']
    mf = ModelFitting(processor)
    configure(mf, simulation)
    mf.set_custom_fitness(simulation.calibration.args['fitness_func_path'])
    fitness = mf.calculate_fitness(simulated_data, target_data)
    assert fitness == expected_fitness
    print('fitness: ', fitness)


@pytest.mark.parametrize('parameter',
                         [

                          ])
def test_fitness(parameter):
    """Test"""
    pass


@pytest.mark.parametrize('parameter',
                         [

                          ])
def test_split_and_update(parameter):
    """Test"""
    pass


@pytest.mark.parametrize('param_array_list',
                         [

                          ])
def test_detector_and_model_update(param_array_list):
    """Test"""
    pass
