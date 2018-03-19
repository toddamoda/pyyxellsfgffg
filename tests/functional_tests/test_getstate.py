import json
from ast import literal_eval
from pathlib import Path

from pyxel.util import objmod as om
from pyxel.io.yaml_processor import load

expected_str = """
parametric.mode='single'
parametric.steps.0.enabled=True
parametric.steps.0.values=[10, 20, 30]
parametric.steps.0.key='pipeline.photon_generation.photon_level.arguments.level'
parametric.steps.1.enabled=True
parametric.steps.1.values=[100, 200, 300]
parametric.steps.1.key='pipeline.charge_generation.tars.arguments.initial_energy'
parametric.steps.2.enabled=False
parametric.steps.3.enabled=False
ccd_process.pipeline.charge_transfer.models.cdm.enabled=False
ccd_process.pipeline.charge_transfer.models.cdm.arguments.beta_p=0.6
ccd_process.pipeline.charge_transfer.models.cdm.arguments.t=0.02048
ccd_process.pipeline.charge_transfer.models.cdm.arguments.svg=1e-10
ccd_process.pipeline.charge_transfer.models.cdm.arguments.beta_s=0.6
ccd_process.pipeline.charge_transfer.models.cdm.arguments.vg=6e-11
ccd_process.pipeline.charge_transfer.models.cdm.arguments.serial_trap_file='pyxel/models/cdm/cdm_euclid_serial.dat'
ccd_process.pipeline.charge_transfer.models.cdm.arguments.st=5e-06
ccd_process.pipeline.charge_transfer.models.cdm.arguments.parallel_trap_file='pyxel/models/cdm/cdm_euclid_parallel.dat'
ccd_process.pipeline.charge_transfer.models.cdm.name='pyxel.models.cdm.CDM.cdm'
ccd_process.pipeline.charge_measurement.models.readout_noise.enabled=False
ccd_process.pipeline.charge_measurement.models.readout_noise.arguments.std_deviation=1.0
ccd_process.pipeline.charge_measurement.models.readout_noise.name='pyxel.models.ccd_noise.add_output_node_noise'
ccd_process.pipeline.charge_collection.models.diffusion.enabled=False
ccd_process.pipeline.charge_collection.models.diffusion.name='pyxel.models.diffusion.diffusion'
ccd_process.pipeline.charge_collection.models.fixed_pattern_noise.enabled=False
ccd_process.pipeline.charge_collection.models.fixed_pattern_noise.arguments.pix_non_uniformity='data/non_uniformity_array_normal_random_dist.data'
ccd_process.pipeline.charge_collection.models.fixed_pattern_noise.name='pyxel.models.ccd_noise.add_fix_pattern_noise'
ccd_process.pipeline.charge_collection.models.full_well.enabled=False
ccd_process.pipeline.charge_collection.models.full_well.arguments.fwc=100
ccd_process.pipeline.charge_collection.models.full_well.name='pyxel.models.full_well.simple_pixel_full_well'
ccd_process.pipeline.photon_generation.models.photon_level.enabled=True
ccd_process.pipeline.photon_generation.models.photon_level.arguments.level=100
ccd_process.pipeline.photon_generation.models.photon_level.name='pyxel.models.photon_generation.add_photon_level'
ccd_process.pipeline.photon_generation.models.shot_noise.enabled=True
ccd_process.pipeline.photon_generation.models.shot_noise.name='pyxel.models.photon_generation.add_shot_noise'
ccd_process.pipeline.photon_generation.models.load_image.enabled=False
ccd_process.pipeline.photon_generation.models.load_image.name='pyxel.models.photon_generation.load_image'
ccd_process.pipeline.charge_generation.models.tars.enabled=True
ccd_process.pipeline.charge_generation.models.tars.arguments.stepping_length=1.0
ccd_process.pipeline.charge_generation.models.tars.arguments.initial_energy=100.0
ccd_process.pipeline.charge_generation.models.tars.arguments.starting_position=['random', 'random', 0.0]
ccd_process.pipeline.charge_generation.models.tars.arguments.incident_angles=['random', 'random']
ccd_process.pipeline.charge_generation.models.tars.arguments.particle_number=10
ccd_process.pipeline.charge_generation.models.tars.name='pyxel.models.tars.tars.run_tars'
ccd_process.pipeline.charge_generation.models.photoelectrons.enabled=False
ccd_process.pipeline.charge_generation.models.photoelectrons.name='pyxel.models.photoelectrons.simple_conversion'
ccd_process.detector.environment.total_ionising_dose=800000000000.0
ccd_process.detector.environment.temperature=300
ccd_process.detector.environment.total_non_ionising_dose=800000000000.0
ccd_process.detector.characteristics.amp=0.8
ccd_process.detector.characteristics.qe=0.5
ccd_process.detector.characteristics.sv=1e-06
ccd_process.detector.characteristics.fwc_serial=30000
ccd_process.detector.characteristics.fwc=20000
ccd_process.detector.characteristics.a2=65536
ccd_process.detector.characteristics.a1=100
ccd_process.detector.characteristics.eta=1
ccd_process.detector.geometry.n_donor=0.0
ccd_process.detector.geometry.pixel_vert_size=10.0
ccd_process.detector.geometry.field_free_thickness=0.0
ccd_process.detector.geometry.col=100
ccd_process.detector.geometry.material='silicon'
ccd_process.detector.geometry.row=100
ccd_process.detector.geometry.bias_voltage=0.0
ccd_process.detector.geometry.pixel_horz_size=10.0
ccd_process.detector.geometry.n_acceptor=0.0
ccd_process.detector.geometry.total_thickness=10.0
ccd_process.detector.geometry.depletion_thickness=10.0
"""


def test_getstate():
    input_filename = 'tests/data/pipeline_parametric.yaml'
    cfg = load(Path(input_filename))

    param_obj = cfg['parametric'].get_state_json()
    proc_obj = cfg['ccd_process'].get_state_json()

    cfg_obj = om.get_state_dict(cfg)
    buf = json.dumps(cfg_obj)
    assert isinstance(buf, str)
    buf = json.dumps(param_obj)
    assert isinstance(buf, str)
    buf = json.dumps(proc_obj)
    assert isinstance(buf, str)


def test_get_state_ids():
    input_filename = 'tests/data/pipeline_parametric.yaml'
    cfg = load(Path(input_filename))
    cfg_obj = om.get_state_dict(cfg)
    result = om.get_state_ids(cfg_obj)
    assert isinstance(result, dict)
    expected = {}
    for line in expected_str.strip().split('\n'):
        key, value = line.split('=')
        expected[key] = literal_eval(value)
    assert len(expected) == len(result)
    for key in expected:
        assert expected[key] == result[key]
    # buf = '\n'.join(['%s=%r' % (key, val) for key, val in result.items()])
    # assert buf.strip() == expected_str.strip()


# test_getstate()
# test_get_state_ids()
