import pytest
import esapy_config.io as io


@pytest.mark.parametrize("yaml_file", [
    'tests/data/pipeline_parametric.yaml',
    'tests/data/test_yaml_new.yaml',
])
def test_yaml_load(yaml_file):
    cfg = io.load(yaml_file)

    assert cfg['simulation'].__class__.__name__ == 'Configuration'
    assert cfg['simulation'].parametric.__class__.__name__ == 'ParametricAnalysis'
    assert cfg['simulation'].parametric.enabled_steps[0].__class__.__name__ == 'ParameterValues'
    assert cfg['simulation'].calibration.__class__.__name__ == 'Calibration'
    assert cfg['detector'].__class__.__name__ == 'CCD'
    assert cfg['detector'].geometry.__class__.__name__ == 'CCDGeometry'
    assert cfg['detector'].environment.__class__.__name__ == 'Environment'
    assert cfg['detector'].material.__class__.__name__ == 'Material'
    assert cfg['detector'].characteristics.__class__.__name__ == 'CCDCharacteristics'
    assert cfg['detector'].charges.__class__.__name__ == 'Charge'
    assert cfg['detector'].photons.__class__.__name__ == 'Photon'
    assert cfg['detector'].pixels.__class__.__name__ == 'Pixel'
    assert cfg['detector'].signal.__class__.__name__ == 'Signal'
    assert cfg['detector'].image.__class__.__name__ == 'Image'
    assert cfg['pipeline'].__class__.__name__ == 'CCDDetectionPipeline'
    # assert cfg['pipeline'].model_groups['photon_generation'].__class__.__name__ == 'ModelGroup'
    # assert cfg['pipeline'].model_groups['photon_generation'].models[0].__class__.__name__ == 'ModelFunction'
    assert cfg['pipeline'].photon_generation.__class__.__name__ == 'ModelGroup'
    assert cfg['pipeline'].photon_generation.models[0].__class__.__name__ == 'ModelFunction'
    assert cfg['pipeline'].charge_generation.__class__.__name__ == 'ModelGroup'
    assert cfg['pipeline'].charge_generation.models[0].__class__.__name__ == 'ModelFunction'
    assert cfg['pipeline'].charge_collection.__class__.__name__ == 'ModelGroup'
    assert cfg['pipeline'].charge_collection.models[0].__class__.__name__ == 'ModelFunction'
    assert cfg['pipeline'].charge_transfer.__class__.__name__ == 'ModelGroup'
    assert cfg['pipeline'].charge_transfer.models[0].__class__.__name__ == 'ModelFunction'
    assert cfg['pipeline'].charge_measurement.__class__.__name__ == 'ModelGroup'
    assert cfg['pipeline'].charge_measurement.models[0].__class__.__name__ == 'ModelFunction'
