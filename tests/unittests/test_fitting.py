"""Unittests for the 'ModelFitting' class."""

import pytest
import numpy as np
import esapy_config as om
import pygmo as pg
from pyxel.calibration.fitting import ModelFitting
from pyxel.detectors.detector import Detector
from pyxel.pipelines.detector_pipeline import DetectionPipeline


def configure(mf, sim):  # , target=None):
    """TBW."""
    pg.set_global_rng_seed(sim.calibration.seed)
    np.random.seed(sim.calibration.seed)
    mf.set_parameters(calibration_mode=sim.calibration.calibration_mode,
                      model_names=sim.calibration.model_names,
                      variables=sim.calibration.variables,
                      var_log=sim.calibration.var_log,
                      generations=sim.calibration.algorithm.generations,
                      population_size=sim.calibration.algorithm.population_size,
                      simulation_output=sim.calibration.output_type,
                      sort_by_var=sim.calibration.sort_var,
                      fitness_func=sim.calibration.fitness_function,
                      champions_file=sim.calibration.champions_file,
                      population_file=sim.calibration.population_file)
    mf.configure(params_per_variable=sim.calibration.params_per_variable,
                 target_output=sim.calibration.target_data_path,
                 target_fit_range=sim.calibration.target_fit_range,
                 out_fit_range=sim.calibration.output_fit_range,
                 weighting=sim.calibration.weighting_path,
                 single_model_input=sim.calibration.single_model_input)


@pytest.mark.parametrize('yaml_file',
                         [
                             'tests/data/calibrate.yaml',
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

    configure(mf, simulation)

    assert mf.is_var_array == [[0], [1, 1, 0], [0]]
    assert mf.is_var_log == [[False], [True, True, False], [False]]
    assert mf.model_name_list == ['characteristics', 'cdm', 'output_node_noise']
    assert mf.params_per_variable == [[1], [2, 2, 1], [1]]
    assert mf.variable_name_lst == [['amp'], ['tr_p', 'nt_p', 'beta_p'], ['std_deviation']]
    assert mf.calibration_mode == 'pipeline'
    assert mf.sim_fit_range == slice(2, 5, None)
    assert mf.targ_fit_range == slice(1, 4, None)
    assert mf.sim_output == 'image'


@pytest.mark.parametrize('yaml',
                         [
                             'tests/data/calibrate_fits.yaml',
                          ])
def test_configure_fits_target(yaml):
    """Test """
    cfg = om.load(yaml)
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
    np.testing.assert_array_equal(mf.all_target_data[0], expected)


@pytest.mark.parametrize('yaml',
                         [
                             'tests/data/calibrate.yaml',
                             'tests/data/calibrate_fits.yaml',
                          ])
def test_boundaries(yaml):
    """Test """
    cfg = om.load(yaml)
    processor = cfg['processor']
    simulation = cfg['simulation']
    mf = ModelFitting(processor)

    configure(mf, simulation)
    mf.set_bound(low_val=simulation.calibration.lower_boundary,
                 up_val=simulation.calibration.upper_boundary)
    lbd_expected = [1.0, -3.0, -3.0, -2.0, -2.0, 0.0, 10.0]
    ubd_expected = [10.0, 0.3010299956639812, 0.3010299956639812, 1.0, 1.0, 1.0, 200.0]
    assert mf.lbd == lbd_expected
    assert mf.ubd == ubd_expected
    l, u = mf.get_bounds()
    assert l == lbd_expected
    assert u == ubd_expected


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
    cfg = om.load('tests/data/calibrate.yaml')
    processor = cfg['processor']
    simulation = cfg['simulation']
    mf = ModelFitting(processor)
    configure(mf, simulation)
    fitness = mf.calculate_fitness(simulated_data, target_data)
    assert fitness == expected_fitness[0]
    print('fitness: ', fitness)


@pytest.mark.parametrize('yaml, factor, expected_fitness',
                         [
                             ('tests/data/calibrate_weighting.yaml', 1., 0.),
                             ('tests/data/calibrate_weighting.yaml', 2., 310815803081.51117),
                             ('tests/data/calibrate_weighting.yaml', 3., 621631606163.0223),
                          ])
def test_weighting(yaml, factor, expected_fitness):
    """Test"""
    pass
    cfg = om.load(yaml)
    processor = cfg['processor']
    simulation = cfg['simulation']
    mf = ModelFitting(processor)
    configure(mf, simulation)
    fitness = mf.calculate_fitness(mf.all_target_data[0]*factor, mf.all_target_data[0])
    assert fitness == expected_fitness
    print('fitness: ', fitness)


def custom_fitness_func(sim, targ):
    """Custom fitness func for testing"""
    return np.sum(targ * 2 - sim / 2 + 1.)


@pytest.mark.parametrize('yaml, simulated_data, target_data, expected_fitness',
                         [
                             ('tests/data/calibrate_custom_fitness.yaml',
                              1., 2., 4.5),
                             ('tests/data/calibrate_custom_fitness.yaml',
                              np.array([1., 2., 3.]), np.array([2., 5., 6.]), 26.),
                             ('tests/data/calibrate_least_squares.yaml',
                              2., 4., 4.),
                          ])
def test_custom_fitness(yaml, simulated_data, target_data, expected_fitness):
    """Test"""
    cfg = om.load(yaml)
    processor = cfg['processor']
    simulation = cfg['simulation']
    mf = ModelFitting(processor)
    configure(mf, simulation)
    fitness = mf.calculate_fitness(simulated_data, target_data)
    assert fitness == expected_fitness
    print('fitness: ', fitness)


@pytest.mark.parametrize('yaml, parameter, expected_fitness',
                         [
                             ('tests/data/calibrate_models.yaml',
                              np.array([1., 0.5, 1.5, -2., -3., 4.5, -4., 1.,
                                        0.5, -1.5, 2., -3., 5., -6., 10., 9.]),
                              185720.6490372545)
                          ])
def test_fitness(yaml, parameter, expected_fitness):
    """Test"""
    cfg = om.load(yaml)
    processor = cfg['processor']
    simulation = cfg['simulation']
    mf = ModelFitting(processor)
    configure(mf, simulation)
    overall_fitness = mf.fitness(parameter)
    assert overall_fitness[0] == expected_fitness
    print('fitness: ', overall_fitness[0])


@pytest.mark.parametrize('yaml, parameter, expected_subarrays',
                         [
                             ('tests/data/calibrate_models.yaml', np.arange(16.),
                              [
                                  0.0,
                                  np.array([10., 100., 1000., 10000.]),
                                  np.array([5., 6., 7., 8.]),
                                  np.array([1.e+09, 1.e+10, 1.e+11, 1.e+12]),
                                  13.0,
                                  1.e+14,
                                  15.0
                               ]),
                          ])
def test_split_and_update(yaml, parameter, expected_subarrays):
    """Test"""
    cfg = om.load(yaml)
    processor = cfg['processor']
    simulation = cfg['simulation']
    mf = ModelFitting(processor)
    configure(mf, simulation)
    subarrays = mf.split_and_update_parameter(parameter)
    for i in range(len(subarrays)):
        np.testing.assert_array_equal(subarrays[i], expected_subarrays[i])


@pytest.mark.parametrize('yaml, param_array_list',
                         [
                             ('tests/data/calibrate_models.yaml',
                              [
                                  1.,
                                  np.array([10., 100., 1000., 10000.]),
                                  np.array([5., 6., 7., 8.]),
                                  np.array([1.e+09, 1.e+10, 1.e+11, 1.e+12]),
                                  13.0,
                                  1.e+14,
                                  150
                               ]),
                          ])
def test_detector_and_model_update(yaml, param_array_list):
    """Test"""
    cfg = om.load(yaml)
    processor = cfg['processor']
    simulation = cfg['simulation']
    mf = ModelFitting(processor)
    configure(mf, simulation)
    mf.update_detector_and_models(param_array_list)
    attributes = [
        mf.det.characteristics.amp,
        mf.pipe.charge_transfer.models[0].arguments['tr_p'],
        mf.pipe.charge_transfer.models[0].arguments['nt_p'],
        mf.pipe.charge_transfer.models[0].arguments['sigma_p'],
        mf.pipe.charge_transfer.models[0].arguments['beta_p'],
        mf.pipe.charge_measurement.models[1].arguments['std_deviation'],
        mf.det.environment.temperature
    ]
    # attributes2 = [
    #     mf.det.characteristics.amp,
    #     mf.pipe.model_groups['charge_transfer'].models[0].arguments['tr_p'],
    #     mf.pipe.model_groups['charge_transfer'].models[0].arguments['nt_p'],
    #     mf.pipe.model_groups['charge_transfer'].models[0].arguments['sigma_p'],
    #     mf.pipe.model_groups['charge_transfer'].models[0].arguments['beta_p'],
    #     mf.pipe.model_groups['charge_measurement'].models[0].arguments['std_deviation'],
    #     mf.det.environment.temperature
    # ]
    for i in range(len(param_array_list)):
        np.testing.assert_array_equal(param_array_list[i], attributes[i])
        # np.testing.assert_array_equal(param_array_list[i], attributes2[i])
