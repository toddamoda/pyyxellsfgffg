import sys
from pathlib import Path

from pyxel.pipelines.model_registry import *

from pyxel import util


CWD = Path(__file__).parent.parent
sys.path.append(str(CWD))


class Arg:

    def __init__(self, name, label=None, validate=None):
        self.name = name
        self.label = label
        self.validate = validate


# @parameter('arg1', label='Argument 1', validate=util.check_range(0, 10, 2))
# @parameter('arg2', label='Argument 2', validate=util.check_choices(['silicon', 'hxrg', 'other']))
# @parameter('arg3', label='Argument 3', validate=Path.is_file)
# @register('photon_generation')
# def my_model(detector, arg1: int, arg2: str, arg3: Path):
#     return detector


# @arguments(
#     Arg('arg1', label='Argument 1', validate=util.check_range(0, 10, 2)),
#     Arg('arg2', label='Argument 2', validate=util.check_choices(['silicon', 'hxrg', 'other'])),
#     Arg('arg3', label='Argument 3', validate=Path.is_file),
# )
# @register('photon_generation')
# def my_model(detector, arg1: int, arg2: str, arg3: Path):
#     print(arg1, arg2, arg3)
#     return detector


# @validate
# @argument('arg1', label='Argument 1', validate=util.check_range(0, 10, 2))
# @argument('arg2', label='Argument 2', validate=util.check_choices(['silicon', 'hxrg', 'other']))
# @argument('arg3', label='Argument 3', validate=Path.is_file)
# @register('photon_generation')
# def my_model(detector, arg1: int, arg2: str, arg3: Path=None):
#     print(arg1, arg2, arg3)
#     return detector
#
#
# def test_parameter():
#     result = my_model("my detector object", 5, 'silicon', 'test.fits')
#     assert result == "my detector object"
#
#
# if __name__ == '__main__':
#     test_parameter()
