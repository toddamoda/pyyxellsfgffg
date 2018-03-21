"""TBW."""
import inspect
import typing as t
from .evaluator import evaluate_reference
from .validator import ValidationError
from .validator import get_validate_info

parameters = {}  # type: t.Dict[str, t.Dict[str, t.Any]]


def validate_arg(func_id: str, name: str, value: t.Any):
    """TBW.

    :param func_id:
    :param name:
    :param value:
    :return:
    """
    func = evaluate_reference(func_id)
    if func.__qualname__.endswith('_validate'):
        func = func.__closure__[0].cell_contents

    if func_id not in parameters:
        return

    params = parameters[func_id]
    validate_enabled = params.get('validate', True)
    convert_enabled = params.get('convert', True)

    if not validate_enabled:
        return

    spec = inspect.getfullargspec(func)
    if convert_enabled:
        if name in spec.annotations:
            arg_type = spec.annotations[name]
            if not isinstance(value, arg_type):
                try:
                    if not isinstance(value, arg_type):
                        value = arg_type(value)
                except ValueError as other_exc:
                    msg = 'Exception: ' + str(other_exc)
                    exc = ValidationError(func_id, name, value, msg)
                    raise exc

    if name in params:
        param = params[name]
        if 'validate' in param:
            validator_func = param['validate']
            extra_info = get_validate_info(validator_func)
            msg = extra_info['error_message'].format(value)

            try:
                is_valid = validator_func(value)
            except Exception as other_exc:
                msg += 'Exception: ' + str(other_exc)
                is_valid = False

            if not is_valid:
                exc = ValidationError(func_id, name, value, msg)
                raise exc


def validate_call(func_id, raise_exception: bool=True, args: list=None, kwargs: dict=None):
    """Validate the arguments passed to the callable.

    :param func_id:
    :param raise_exception: optional output list that is appended if validation
        errors are found.
    :param args: mutable list of positional arguments
    :param kwargs: mutable dict of keyword arguments
    :return: a list of exceptions
    :raises: ValidationError
    """
    if args is None:
        args = []

    if kwargs is None:
        kwargs = {}

    errors = []  # type: t.List[ValidationError]

    func = evaluate_reference(func_id)
    if func.__qualname__.endswith('_validate'):
        func = func.__closure__[0].cell_contents

    if func_id not in parameters:
        return errors

    params = parameters[func_id]
    validate_enabled = params.get('validate', True)
    convert_enabled = params.get('convert', True)

    if not validate_enabled:
        return errors

    # TODO: refactor - too long and complicated
    spec = inspect.getfullargspec(func)
    if spec.defaults is not None:
        start = len(spec.args) - len(spec.defaults)
        default_values = dict(zip(spec.args[start:], spec.defaults))
    else:
        default_values = {}

    if convert_enabled:
        for i, name in enumerate(spec.args):
            if name in spec.annotations:
                arg_type = spec.annotations[name]
                value = None
                try:
                    if name in kwargs:
                        value = kwargs[name]
                        if not isinstance(value, arg_type):
                            kwargs[name] = arg_type(value)

                    elif i < len(args):
                        value = args[i]
                        if not isinstance(value, arg_type):
                            args[i] = arg_type(value)
                except ValueError as other_exc:
                    msg = 'Exception: ' + str(other_exc)
                    exc = ValidationError(func_id, name, value, msg)
                    if raise_exception:
                        raise exc
                    errors.append(exc)

    if len(errors) == 0:
        for i, name in enumerate(spec.args):
            if name in params:
                value = None
                if name in default_values:
                    value = default_values[name]

                if name in kwargs:
                    value = kwargs[name]
                elif i < len(args):
                    value = args[i]

                param = params[name]
                if 'validate' in param:
                    validator_func = param['validate']
                    extra_info = get_validate_info(validator_func)
                    msg = extra_info['error_message'].format(value)

                    try:
                        is_valid = validator_func(value)
                    except Exception as other_exc:
                        msg += 'Exception: ' + str(other_exc)
                        is_valid = False

                    if not is_valid:
                        exc = ValidationError(func_id, name, value, msg)
                        if raise_exception:
                            raise exc
                        errors.append(exc)
    return errors


def validate(func):
    """TBW."""
    def _validate(*args, **kwargs):
        """TBW."""
        func_id = func.__module__ + '.' + func.__name__
        args = list(args)
        validate_call(func_id, True, args, kwargs)
        return func(*args, **kwargs)

    return _validate


def argument(name, **kwargs):
    """TBW."""
    def _register(func):
        """TBW."""
        func_id = func.__module__ + '.' + func.__name__
        if func_id not in parameters:
            parameters[func_id] = {}
        param = dict(kwargs)
        parameters[func_id][name] = param
        return func

    return _register
