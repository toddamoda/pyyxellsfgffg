"""Unittests for the 'ModelFitting' class."""
import esapy_config.io as io
import numpy as np
import pytest

try:
    import pygmo as pg
    WITH_PYGMO = True
except ImportError:
    WITH_PYGMO = False

from pyxel.calibration.fitting import ModelFitting
from pyxel.pipelines.processor import Processor


def configure(mf, sim):
    """TBW."""
    pg.set_global_rng_seed(sim.calibration.seed)
    np.random.seed(sim.calibration.seed)
    settings = {
        'calibration_mode': sim.calibration.calibration_mode,
        'generations': sim.calibration.algorithm.generations,
        'population_size': sim.calibration.algorithm.population_size,
        'simulation_output': sim.calibration.result_type,
        'fitness_func': sim.calibration.fitness_function,
        'target_output': sim.calibration.target_data_path,
        'target_fit_range': sim.calibration.target_fit_range,
        'out_fit_range': sim.calibration.result_fit_range,
        'weighting': sim.calibration.weighting_path,
        'champions_file': None,
        'population_file': None
    }
    mf.configure(settings)


@pytest.mark.skipif(not WITH_PYGMO, reason="Package 'pygmo' is not installed.")
@pytest.mark.parametrize('yaml_file',
                         [
                             'tests/data/calibrate.yaml',
                         ])
def test_configure_params(yaml_file):
    """Test """
    cfg = io.load(yaml_file)
    detector = cfg['ccd_detector']
    pipeline = cfg['pipeline']
    processor = Processor(detector, pipeline)
    simulation = cfg['simulation']
    mf = ModelFitting(processor, simulation.calibration.parameters)

    if not isinstance(mf.processor, Processor):
        raise ValueError

    configure(mf, simulation)

    assert mf.calibration_mode == 'pipeline'
    assert mf.sim_fit_range == slice(2, 5, None)
    assert mf.targ_fit_range == slice(1, 4, None)
    assert mf.sim_output == 'image'


@pytest.mark.skipif(not WITH_PYGMO, reason="Package 'pygmo' is not installed.")
@pytest.mark.parametrize('yaml',
                         [
                             'tests/data/calibrate_fits.yaml',
                         ])
def test_configure_fits_target(yaml):
    """Test """
    cfg = io.load(yaml)
    detector = cfg['ccd_detector']
    pipeline = cfg['pipeline']
    processor = Processor(detector, pipeline)
    simulation = cfg['simulation']
    mf = ModelFitting(processor, simulation.calibration.parameters)
    configure(mf, simulation)
    assert mf.sim_fit_range == (slice(2, 5, None), slice(4, 7, None))
    assert mf.targ_fit_range == (slice(1, 4, None), slice(5, 8, None))
    assert mf.sim_output == 'image'
    expected = np.array([[3858.44799859, 3836.11204939, 3809.85008514],
                         [4100.87410744, 4053.26348117, 4018.33656962],
                         [4233.53215652, 4021.60164244, 3969.79740826]])
    np.testing.assert_array_equal(np.around(mf.all_target_data[0], decimals=4),
                                  np.around(expected, decimals=4))


@pytest.mark.skipif(not WITH_PYGMO, reason="Package 'pygmo' is not installed.")
@pytest.mark.parametrize('yaml',
                         [
                             'tests/data/calibrate.yaml',
                             'tests/data/calibrate_fits.yaml',
                         ])
def test_boundaries(yaml):
    """Test """
    cfg = io.load(yaml)
    detector = cfg['ccd_detector']
    pipeline = cfg['pipeline']
    processor = Processor(detector, pipeline)
    simulation = cfg['simulation']
    mf = ModelFitting(processor, simulation.calibration.parameters)

    configure(mf, simulation)

    lbd_expected = [1.0, -3.0, -3.0, -2.0, -2.0, 0.0, 10.0]
    ubd_expected = [10.0, 0.3010299956639812, 0.3010299956639812, 1.0, 1.0, 1.0, 200.0]
    assert mf.lbd == lbd_expected
    assert mf.ubd == ubd_expected
    ll, uu = mf.get_bounds()
    assert ll == lbd_expected
    assert uu == ubd_expected


@pytest.mark.skipif(not WITH_PYGMO, reason="Package 'pygmo' is not installed.")
@pytest.mark.parametrize('simulated_data, target_data, expected_fitness',
                         [
                             (231, 231, 0.),
                             (231, 145, 86.),
                             (2.31, 1.45, 0.8600000000000001),
                             (2., 1, 1.0),
                             (np.array([1, 9, 45, 548, 2, 2]), np.array([1, 9, 45, 548, 2, 2]), 0.),
                             (np.array([1, 9, 45, 548, 2, 2]), np.array([1, 3, 56, 21, 235, 11]), 786.),
                             (np.array([[1362., 1378.], [1308., 1309.]]),
                              np.array([[1362., 1378.], [1308., 1309.]]), 0.),
                             (np.array([[1362., 1378.],
                                        [1308., 1309.]]),
                              np.array([[1462., 1368.],
                                        [1508., 1399.]]), 400.)
                         ])
def test_calculate_fitness(simulated_data, target_data, expected_fitness):
    """Test"""
    cfg = io.load('tests/data/calibrate.yaml')
    detector = cfg['ccd_detector']
    pipeline = cfg['pipeline']
    processor = Processor(detector, pipeline)
    simulation = cfg['simulation']
    mf = ModelFitting(processor, simulation.calibration.parameters)
    configure(mf, simulation)
    fitness = mf.calculate_fitness(simulated_data, target_data)
    assert fitness == expected_fitness
    print('fitness: ', fitness)


@pytest.mark.skipif(not WITH_PYGMO, reason="Package 'pygmo' is not installed.")
@pytest.mark.parametrize('yaml, factor, expected_fitness',
                         [
                             ('tests/data/calibrate_weighting.yaml', 1, 0.),
                             ('tests/data/calibrate_weighting.yaml', 2, 310815803081.51117),
                             ('tests/data/calibrate_weighting.yaml', 3, 621631606163.0223),
                         ])
def test_weighting(yaml, factor, expected_fitness):
    """Test"""
    cfg = io.load(yaml)
    detector = cfg['ccd_detector']
    pipeline = cfg['pipeline']
    processor = Processor(detector, pipeline)
    simulation = cfg['simulation']
    mf = ModelFitting(processor, simulation.calibration.parameters)
    configure(mf, simulation)
    fitness = mf.calculate_fitness(mf.all_target_data[0]*factor, mf.all_target_data[0])
    assert fitness == expected_fitness
    print('fitness: ', fitness)


def custom_fitness_func(sim, targ):
    """Custom fitness func for testing"""
    return np.sum(targ * 2 - sim / 2 + 1.)


@pytest.mark.skipif(not WITH_PYGMO, reason="Package 'pygmo' is not installed.")
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
    cfg = io.load(yaml)
    detector = cfg['ccd_detector']
    pipeline = cfg['pipeline']
    processor = Processor(detector, pipeline)
    simulation = cfg['simulation']
    mf = ModelFitting(processor, simulation.calibration.parameters)
    configure(mf, simulation)
    fitness = mf.calculate_fitness(simulated_data, target_data)
    assert fitness == expected_fitness
    print('fitness: ', fitness)


@pytest.mark.skipif(not WITH_PYGMO, reason="Package 'pygmo' is not installed.")
@pytest.mark.parametrize('yaml, parameter, expected_fitness',
                         [
                             ('tests/data/calibrate_models.yaml',
                              np.array([1., 0.5, 1.5, -2., -3., 4.5, -4., 1.,
                                        0.5, -3.5, 2., -3., -4., 0.5, 1., 100.]),
                              88431.18016117143)
                         ])
def test_fitness(yaml, parameter, expected_fitness):
    """Test"""
    cfg = io.load(yaml)
    detector = cfg['ccd_detector']
    pipeline = cfg['pipeline']
    processor = Processor(detector, pipeline)
    simulation = cfg['simulation']
    mf = ModelFitting(processor, simulation.calibration.parameters)
    configure(mf, simulation)
    overall_fitness = mf.fitness(parameter)
    assert overall_fitness[0] == expected_fitness
    print('fitness: ', overall_fitness[0])


@pytest.mark.skipif(not WITH_PYGMO, reason="Package 'pygmo' is not installed.")
@pytest.mark.parametrize('yaml, parameter, expected_array',
                         [
                             ('tests/data/calibrate_models.yaml', np.arange(16.),
                              np.array([0.0,
                                        10., 100., 1000., 10000.,
                                        5., 6., 7., 8.,
                                        1.e+09, 1.e+10, 1.e+11, 1.e+12,
                                        13.0,
                                        1.e+14,
                                        15.0])
                              ),
                         ])
def test_split_and_update(yaml, parameter, expected_array):
    """Test"""
    cfg = io.load(yaml)
    detector = cfg['ccd_detector']
    pipeline = cfg['pipeline']
    processor = Processor(detector, pipeline)
    simulation = cfg['simulation']
    mf = ModelFitting(processor, simulation.calibration.parameters)
    configure(mf, simulation)
    array = mf.update_parameter(parameter)
    np.testing.assert_array_equal(array, expected_array)


@pytest.mark.skipif(not WITH_PYGMO, reason="Package 'pygmo' is not installed.")
@pytest.mark.parametrize('yaml, param_array',
                         [
                             ('tests/data/calibrate_models.yaml',
                              np.array([1.,
                                        10., 100., 1000., 10000.,
                                        5., 6., 7., 8.,
                                        1.e+09, 1.e+10, 1.e+11, 1.e+12,
                                        13.0,
                                        1.e+14,
                                        150])
                              ),
                         ])
def test_detector_and_model_update(yaml, param_array):
    """Test"""
    cfg = io.load(yaml)
    detector = cfg['ccd_detector']
    pipeline = cfg['pipeline']
    processor = Processor(detector, pipeline)
    simulation = cfg['simulation']
    mf = ModelFitting(processor, simulation.calibration.parameters)
    configure(mf, simulation)
    mf.processor = mf.update_processor(param_array)
    attributes = [
        mf.processor.detector.characteristics.amp,
        mf.processor.pipeline.charge_transfer.models[0].arguments['tr_p'],
        mf.processor.pipeline.charge_transfer.models[0].arguments['nt_p'],
        mf.processor.pipeline.charge_transfer.models[0].arguments['sigma_p'],
        mf.processor.pipeline.charge_transfer.models[0].arguments['beta_p'],
        mf.processor.pipeline.charge_measurement.models[1].arguments['std_deviation'],
        mf.processor.detector.environment.temperature
    ]
    a = 0
    for attr in attributes:
        if isinstance(attr, np.ndarray):
            b = len(attr)
            np.testing.assert_array_equal(attr, param_array[a:a + b])
        else:
            b = 1
            assert attr == param_array[a]
        a += b
