from pathlib import Path
import yaml
import esapy_config as om

from pyxel.detectors.environment import Environment

CWD_PATH = Path(__file__).parent.parent.parent


def test_gui_def():
    gui_file = CWD_PATH.joinpath('pyxel', 'web', 'gui.yaml')  # TODO: hardcoded
    with gui_file.open() as fd:
        cfg = yaml.load(fd)

    serializer = om.serializer.pyxel_gui.Serializer(Environment)
    cfg2 = serializer.to_dict()
    buf = serializer.serialize()
    print(buf)
    return


if __name__ == '__main__':
    test_gui_def()
