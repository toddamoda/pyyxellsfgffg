import pytest
import esapy_config.io as io

try:
    import pygmo as pg
    WITH_PYGMO = True
except ImportError:
    WITH_PYGMO = False


@pytest.mark.skipif(not WITH_PYGMO, reason="Package 'pygmo' is not installed.")
@pytest.mark.parametrize("yaml_file", [
    'tests/data/parametric.yaml',
    'tests/data/yaml.yaml',
])
def test_yaml_load(yaml_file):
    cfg = io.load(yaml_file)

    assert cfg['simulation'].__class__.__name__ == 'Configuration'
    assert cfg['simulation'].parametric.__class__.__name__ == 'ParametricAnalysis'
    assert cfg['simulation'].parametric.enabled_steps[0].__class__.__name__ == 'ParameterValues'
    assert cfg['simulation'].calibration.__class__.__name__ == 'Calibration'
    assert cfg['ccd_detector'].__class__.__name__ == 'CCD'
    assert cfg['ccd_detector'].geometry.__class__.__name__ == 'CCDGeometry'
    assert cfg['ccd_detector'].environment.__class__.__name__ == 'Environment'
    assert cfg['ccd_detector'].material.__class__.__name__ == 'Material'
    assert cfg['ccd_detector'].characteristics.__class__.__name__ == 'CCDCharacteristics'
    assert cfg['ccd_detector'].charge.__class__.__name__ == 'Charge'
    assert cfg['ccd_detector'].photon.__class__.__name__ == 'Photon'
    assert cfg['ccd_detector'].pixel.__class__.__name__ == 'Pixel'
    assert cfg['ccd_detector'].signal.__class__.__name__ == 'Signal'
    assert cfg['ccd_detector'].image.__class__.__name__ == 'Image'
    assert cfg['pipeline'].__class__.__name__ == 'DetectionPipeline'
    # assert cfg['pipeline'].__class__.__name__ == 'CCDDetectionPipeline'
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
