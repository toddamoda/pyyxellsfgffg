from pathlib import Path
# import pytest
import esapy_config as om


CWD = Path(__file__).parent.parent


def test_yaml_load():
    yaml_file = CWD.joinpath('data', 'test_yaml_new.yaml')
    cfg = om.load(yaml_file)

    assert cfg['simulation'].__class__.__name__ == 'Configuration'
    assert cfg['simulation'].parametric_analysis.steps[0].__class__.__name__ == 'StepValues'
    assert cfg['detector'].__class__.__name__ == 'CCD'
    assert cfg['detector'].geometry.__class__.__name__ == 'CCDGeometry'
    assert cfg['pipeline'].__class__.__name__ == 'CCDDetectionPipeline'
    # assert cfg['pipeline'].model_groups['photon_generation'].__class__.__name__ == 'ModelGroup'
    # assert cfg['pipeline'].model_groups['photon_generation'].models[0].__class__.__name__ == 'ModelFunction'
    assert cfg['pipeline'].photon_generation.__class__.__name__ == 'ModelGroup'
    assert cfg['pipeline'].photon_generation.models[0].__class__.__name__ == 'ModelFunction'

# # @pytest.mark.skip(reason="much too difficult to maintain")
# def test_yaml_dump():
#
#     yaml_file = CWD.joinpath('data', 'test_yaml_new.yaml')
#     cfg = om.load(yaml_file)
#     result = om.dump(cfg)
#     yaml_expected = CWD.joinpath('data', 'test_yaml_new_dump_expected.yaml').open('r').read()
#     for i in range(len(result)):
#         if yaml_expected[i] != result[i]:
#             pass
#     assert result == yaml_expected
#
#     print(result)
