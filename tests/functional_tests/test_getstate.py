# from ast import literal_eval
# from pathlib import Path
# import esapy_config.io as io
# from esapy_config import get_state_ids, get_state_dict
#
# expected_str = """
# processor.detector.characteristics.a2=65536
# processor.detector.characteristics.sv=1e-06
# processor.detector.characteristics.qe=0.5
# processor.detector.characteristics.eta=1
# processor.detector.characteristics.fwc=20000
# processor.detector.characteristics.amp=0.8
# processor.detector.characteristics.a1=100
# processor.detector.characteristics.fwc_serial=30000
# processor.detector.environment.temperature=300
# processor.detector.environment.total_ionising_dose='8.0e11'
# processor.detector.environment.total_non_ionising_dose='8.0e11'
# processor.detector.material.n_donor=0.0
# processor.detector.material.material='silicon'
# processor.detector.material.n_acceptor=0.0
# processor.detector.geometry.row=100
# processor.detector.geometry.total_thickness=10.0
# processor.detector.geometry.pixel_horz_size=10.0
# processor.detector.geometry.pixel_vert_size=10.0
# processor.detector.geometry.col=100
# processor.pipeline.charge_collection.0.enabled=False
# processor.pipeline.charge_collection.0.name='fixed_pattern_noise'
# processor.pipeline.charge_collection.0.func='pyxel.models.charge_collection.fix_pattern_noise.fix_pattern_noise'
# processor.pipeline.charge_collection.0.arguments.pix_non_uniformity='data/non_uniformity_array_normal_random_dist.data'
# processor.pipeline.charge_collection.1.enabled=False
# processor.pipeline.charge_collection.1.name='full_well'
# processor.pipeline.charge_collection.1.func='pyxel.models.charge_collection.full_well.simple_pixel_full_well'
# processor.pipeline.photon_generation.0.enabled=False
# processor.pipeline.photon_generation.0.name='load_image'
# processor.pipeline.photon_generation.0.func='pyxel.models.photon_generation.load_image.load_image'
# processor.pipeline.photon_generation.1.enabled=True
# processor.pipeline.photon_generation.1.name='photon_level'
# processor.pipeline.photon_generation.1.func='pyxel.models.photon_generation.illumination.illumination'
# processor.pipeline.photon_generation.1.arguments.level=100
# processor.pipeline.photon_generation.2.enabled=True
# processor.pipeline.photon_generation.2.name='shot_noise'
# processor.pipeline.photon_generation.2.func='pyxel.models.photon_generation.shot_noise.shot_noise'
# processor.pipeline.charge_transfer.0.enabled=False
# processor.pipeline.charge_transfer.0.name='cdm'
# processor.pipeline.charge_transfer.0.func='pyxel.models.charge_transfer.cdm.CDM.cdm'
# processor.pipeline.charge_transfer.0.arguments.t=0.02048
# processor.pipeline.charge_transfer.0.arguments.svg=1e-10
# processor.pipeline.charge_transfer.0.arguments.parallel_trap_file='pyxel/models/cdm/cdm_euclid_parallel.dat'
# processor.pipeline.charge_transfer.0.arguments.serial_trap_file='pyxel/models/cdm/cdm_euclid_serial.dat'
# processor.pipeline.charge_transfer.0.arguments.vg=6e-11
# processor.pipeline.charge_transfer.0.arguments.beta_s=0.6
# processor.pipeline.charge_transfer.0.arguments.beta_p=0.6
# processor.pipeline.charge_transfer.0.arguments.st=5e-06
# processor.pipeline.charge_measurement.0.enabled=False
# processor.pipeline.charge_measurement.0.name='output_node_noise'
# processor.pipeline.charge_measurement.0.func='pyxel.models.charge_measurement.readout_noise.output_node_noise'
# processor.pipeline.charge_measurement.0.arguments.std_deviation=1.0
# processor.pipeline.charge_generation.0.enabled=False
# processor.pipeline.charge_generation.0.name='photoelectrons'
# processor.pipeline.charge_generation.0.func='pyxel.models.charge_generation.photoelectrons.simple_conversion'
# processor.pipeline.charge_generation.1.enabled=True
# processor.pipeline.charge_generation.1.name='tars'
# processor.pipeline.charge_generation.1.func='pyxel.models.tars.tars.run_tars'
# processor.pipeline.charge_generation.1.arguments.particle_number=10
# processor.pipeline.charge_generation.1.arguments.spectrum_file='pyxel/models/charge_generation/tars/data/inputs/proton_L2_solarMax_11mm_Shielding.txt'
# processor.pipeline.charge_generation.1.arguments.initial_energy=100.0
# processor.pipeline.charge_generation.1.arguments.particle_type='proton'
# processor.pipeline.charge_generation.1.arguments.let_file='pyxel/models/tars/data/inputs/let_proton_1GeV_100um_geant4_HighResHist.ascii'
# parametric.mode='single'
# parametric.steps.0.key='pipeline.photon_generation.photon_level.arguments.level'
# parametric.steps.0.enabled=True
# parametric.steps.0.values=[10, 20, 30]
# parametric.steps.1.key='pipeline.charge_generation.tars.arguments.initial_energy'
# parametric.steps.1.enabled=True
# parametric.steps.1.values=[100, 200, 300]
# parametric.steps.2.enabled=False
# parametric.steps.3.enabled=False
# """
#
#
# # def test_getstate():                                                 # todo reactivate this test
# #     input_filename = 'tests/data/pipeline_parametric.yaml'
# #     cfg = io.load(Path(input_filename))
# #
# #     param_obj = cfg['simulation'].parametric.get_state_json()
# #     proc_obj = cfg['processor'].get_state_json()
# #
# #     cfg_obj = om.get_state_dict(cfg)
# #     buf = json.dumps(cfg_obj)
# #     assert isinstance(buf, str)
# #     buf = json.dumps(param_obj)
# #     assert isinstance(buf, str)
# #     buf = json.dumps(proc_obj)
# #     assert isinstance(buf, str)
#
#
# def test_get_state_ids():
#     input_filename = 'tests/data/pipeline_parametric.yaml'
#     cfg = io.load(Path(input_filename))
#     cfg_obj = get_state_dict(cfg)
#     result = get_state_ids(cfg_obj)
#     assert isinstance(result, dict)
#     expected = {}
#     for line in expected_str.strip().split('\n'):
#         key, value = line.split('=')
#         expected[key] = literal_eval(value)
#     # assert len(expected) == len(result)
#     # for key in expected:
#     #     print(key)
#     #     assert expected[key] == result[key]
#     # buf = '\n'.join(['%s=%r' % (key, val) for key, val in result.items()])
#     # assert buf.strip() == expected_str.strip()
