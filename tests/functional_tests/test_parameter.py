import sys
from pathlib import Path

import pyxel

from pyxel import util


CWD = Path(__file__).parent.parent
sys.path.append(str(CWD))


@pyxel.validate
@pyxel.argument('even_value', label='Argument 1', validate=util.check_range(0, 10, 2))
@pyxel.argument('file_value', label='Argument 2', validate=Path.is_file)
@pyxel.argument('choice_value', label='Argument 3', validate=util.check_choices(['silicon', 'hxrg', 'other']))
# @register('photon_generation')
def my_model_with_validate(detector, even_value: int, file_value: Path, choice_value: str='silicon'):
    print(even_value, choice_value, file_value)
    return detector


@pyxel.argument('even_value', label='Argument 1', validate=util.check_range(0, 10, 2))
@pyxel.argument('file_value', label='Argument 2', validate=Path.is_file)
@pyxel.argument('choice_value', label='Argument 3', validate=util.check_choices(['silicon', 'hxrg', 'other']))
# @register('photon_generation')
def my_model_no_validate(detector, even_value: int, file_value: Path, choice_value: str='silicon'):
    print(even_value, choice_value, file_value)
    return detector


def test_argument_validation():

    if '__main__.my_model_with_validate' in pyxel.parameters:
        model_with_validate_id = '__main__.my_model_with_validate'
    else:
        # when run with pytest
        model_with_validate_id = 'tests.functional_tests.test_parameter.my_model_with_validate'

    #
    # test that validator catches uneven value
    #
    try:
        my_model_with_validate("my detector object", 5, Path(__file__), 'silicon')
    except pyxel.ValidationError as exc:
        assert exc.arg == 'even_value'

    #
    # test that validator returns aok
    #
    result = my_model_with_validate("my detector object", 6, Path(__file__), 'silicon')
    assert result == "my detector object"

    #
    # test that incorrect argument is ignored in a model that does not have the @validate
    #
    my_model_no_validate("my detector object", 5, Path(__file__), 'silicon')

    #
    # test validation can be switched off and on
    #
    pyxel.parameters[model_with_validate_id]['validate'] = False
    my_model_with_validate("my detector object", 6, Path(__file__), 'bad-choice')
    pyxel.parameters[model_with_validate_id]['validate'] = True
    try:
        my_model_with_validate("my detector object", 6, Path(__file__), 'bad-choice')
    except pyxel.ValidationError as exc:
        assert exc.arg == 'choice_value'

    #
    # test that annotation argument conversion takes place on the __file__ argument
    #
    my_model_with_validate("my detector object", 6, __file__, 'silicon')  # default convert is True
    pyxel.parameters[model_with_validate_id]['convert'] = False
    try:
        my_model_with_validate("my detector object", 6, __file__, 'silicon')
    except Exception as exc:
        print(exc)
        pyxel.parameters[model_with_validate_id]['convert'] = True
    my_model_with_validate("my detector object", 6, __file__, 'silicon')


if __name__ == '__main__':
    test_argument_validation()
