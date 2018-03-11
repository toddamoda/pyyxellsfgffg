from pathlib import Path
import yaml

from pyxel import util
from pyxel.io.yaml_processor_new import PyxelLoader


CWD = Path(__file__).parent.parent


def test_yaml_new():
    yaml_file = CWD.joinpath('data', 'test_yaml_new.yaml')
    with open(str(yaml_file)) as file_obj:
        cfg = yaml.load(file_obj, Loader=PyxelLoader)

    print(cfg)


if __name__ == '__main__':
    test_yaml_new()


# cfg = load in a template yaml file
# pipeline = get referecnce to DetectionPipeline instance
# construct many ModelFunctions (or existing)
# ModelFunction(name, func, arg, tec)
# pipeline.charge_generation.add_model(xxxx)
# pipeline.charge_generation.add_model(yyyy)
# pipeline.photon_generation.add_model(xxxz)
# ..
# ..
# yaml.dump(cfg) = >save to yaml file => DONE!
