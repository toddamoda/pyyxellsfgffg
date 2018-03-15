import sys
from pathlib import Path

import pyxel

from pyxel import util
from pyxel.io.yaml_processor_new import load_config


CWD = Path(__file__).parent.parent
sys.path.append(str(CWD))


@pyxel.validate
@pyxel.argument('even_value', label='Argument 1', validate=pyxel.check_range(0, 10, 2))
@pyxel.argument('file_value', label='Argument 2', validate=Path.is_file)
@pyxel.argument('choice_value', label='Argument 3', validate=pyxel.check_choices(['silicon', 'hxrg', 'other']))
# @register('photon_generation')
def my_model_with_validate(detector, even_value: int, file_value: Path, choice_value: str='silicon'):
    # print(even_value, choice_value, file_value)
    return detector


@pyxel.argument('even_value', label='Argument 1', validate=pyxel.check_range(0, 10, 2))
@pyxel.argument('file_value', label='Argument 2', validate=Path.is_file)
@pyxel.argument('choice_value', label='Argument 3', validate=pyxel.check_choices(['silicon', 'hxrg', 'other']))
# @register('photon_generation')
def my_model_no_validate(detector, even_value: int, file_value: Path, choice_value: str='silicon'):
    # print(even_value, choice_value, file_value)
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


def test_model_validation():

    if '__main__.my_model_with_validate' in pyxel.parameters:
        model_with_validate_id = '__main__.my_model_with_validate'
    else:
        # when run with pytest
        model_with_validate_id = 'tests.functional_tests.test_parameter.my_model_with_validate'

    args = {
        'even_value': 6,
        'file_value': __file__,
        'choice_value': 'silicon',

    }
    model = pyxel.ModelFunction('my_model', model_with_validate_id, arguments=args)

    #
    # Test the aok situation
    #
    pyxel.validate_call(model_with_validate_id, kwargs=model.arguments)

    #
    # Introduce an error and catch an exception
    #
    model.arguments['even_value'] = 5
    model.arguments['choice_value'] = 'xxx'
    try:
        pyxel.validate_call(model_with_validate_id, kwargs=model.arguments)
    except pyxel.ValidationError as exc:
        assert exc.arg == 'even_value'

    #
    # Disable raising an exception and collect all the ValidationError(s)
    #
    errors = []
    errors += pyxel.validate_call(model_with_validate_id, False, kwargs=model.arguments)
    assert len(errors) == 2


def test_processor_validate():
    yaml_file = CWD.joinpath('data', 'test_yaml_new.yaml')
    cfg = load_config(yaml_file)

    processor = cfg['processor']
    processor.pipeline.set_model_enabled('*', False)
    model = processor.pipeline.photon_generation.photon_level

    #
    # Test an invalid range argument, but a disabled model
    #
    model.arguments['level'] = -1.5
    errors = processor.validate()
    assert len(errors) == 0

    #
    # Test an invalid range argument with a model that is enabled
    #
    model.enabled = True
    model.arguments['level'] = -10
    errors = processor.validate()
    assert len(errors) == 1

    #
    # Test valid argument
    #
    model.arguments['level'] = 100
    errors = processor.validate()
    assert len(errors) == 0

    #
    # Test valid argument that will be converted to an int
    #
    model.arguments['level'] = 1.5
    errors = processor.validate()
    assert len(errors) == 0
    assert model.arguments['level'] == 1

    #
    # Test invalid argument that cannot be converted to an int
    #
    model.arguments['level'] = 'fred'
    errors = processor.validate()
    assert len(errors) == 1
    assert model.arguments['level'] == 'fred'


if __name__ == '__main__':
    test_argument_validation()
    test_model_validation()
    test_processor_validate()
