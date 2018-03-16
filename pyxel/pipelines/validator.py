"""Validation functions and decorators."""

import inspect

import typing as t  # noqa: F401

import attr

from pyxel import util


parameters = {}  # type: t.Dict[str, t.Dict[str, t.Any]]


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


class ValidationError(Exception):
    """Exception thrown by the argument validate function."""

    def __init__(self, func, arg, value, msg=''):
        """TBW."""
        self.func = func
        self.arg = arg
        self.value = value
        self.msg = msg

    def __repr__(self):
        """TBW."""
        return 'ValidationError(%(name)r, %(func)r, %(arg)r, %(value)r, %(msg)r)' % vars(self)

    def __str__(self):
        """TBW."""
        msg = 'Validation failed for function: %(func)r, arg: %(arg)r, value: %(value)r, msg: %(msg)r'
        msg = msg % vars(self)
        return msg


def validate_arg(func_id, name, value):
    """TBW.

    :param func_id:
    :param name:
    :param value:
    :return:
    """
    func = util.evaluate_reference(func_id)
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

    func = util.evaluate_reference(func_id)
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


def get_validate_info(func):
    """Retrieve the extra information dict from a validator."""
    return getattr(func, 'validate_info', {'error_message': 'Bad value: {}. '})


def check_choices(choices: list):
    """TBW.

    :param choices:
    :return:
    """
    def _wrapper(value):
        return value in choices

    # NOTE: _wrapper.__closure__[0].cell_contents => ['silicon', 'hxrg', 'other']
    info = {
        'error_message': 'Expected: %r, got: {}. ' % choices,
        'choices': choices,
    }
    setattr(_wrapper, 'validate_info', info)
    return _wrapper


def check_range(min_val, max_val, step=None):
    """TBW.

    :param min_val:
    :param max_val:
    :param step:
    """
    def _wrapper(value):
        """TBW."""
        # Do something
        result = False
        if min_val <= value <= max_val:
            result = True
            if step:
                multiplier = 1
                if isinstance(step, float):
                    # In Python3: 1.2 % 0.1 => 0.0999999999999999
                    # but it should be 0.0
                    # To fix this, we multiply by a factor that essentially
                    # converts the float into an int

                    # get digits after decimal.
                    # NOTE: the decimal.Decimal class cannot do this properly in Python 3.
                    exp = len(format(step, '.8f').strip('0').split('.')[1])
                    multiplier = 10 ** exp
                result = ((value * multiplier) % (step * multiplier)) == 0
        return result

    info = {
        'error_message': 'Expected value in range: %r to %r in %r steps, got: {}. ' % (min_val, max_val, step),
        'min_val': min_val, 'max_val': max_val, 'step': step
    }
    setattr(_wrapper, 'validate_info', info)

    return _wrapper


attr_class = attr.s


def attr_def(doc: str=None, readonly: bool=False, label: str=None, units: str=None, check: t.Callable=None,
             *args, **kwargs):
    """Class attribute definition.

    :param doc:
    :param readonly:
    :param label:
    :param units:
    :param check:
    :param args: arguments sent to attr.ib
    :param kwargs: keyword arguments sent to attr.ib
    :return:
    """
    metadata = kwargs.get('metadata', {})
    metadata['validate'] = check
    metadata['doc'] = doc
    metadata['readonly'] = readonly
    metadata['label'] = label
    metadata['units'] = units

    kwargs['metadata'] = metadata

    att = attr.ib(*args, **kwargs)

    return att


@attr_class
class AttrClass:
    """Class that validates all assignments to attributes."""

    def __setattr__(self, key: str, value: t.Any):
        """Validate value.

        :param key:
        :param value:
        """
        if key in self.__dict__:
            # handle the attribute assignment case
            att = getattr(attr.fields(type(self)), key)
            if att:
                msg = ''
                att_id = self.__module__ + '.' + self.__class__.__name__ + '.' + key
                is_valid = True
                convert_enabled = True  # TODO: may be make this a meta parameter?
                if convert_enabled:
                    if att.type and not isinstance(value, att.type):
                        try:
                            value = att.type(value)
                        except ValueError as other_exc:
                            msg = 'Exception: ' + str(other_exc)
                            exc = ValidationError(att_id, key, value, msg)
                            raise exc

                # check if the attr.ib validator is set, if so, use it
                if att.validator:
                    is_valid = att.validator(self, att, value)

                # check if our own value validator is set, if so, use it.
                validator_func = att.metadata.get('validate')
                if validator_func:
                    extra_info = get_validate_info(validator_func)
                    msg = extra_info['error_message'].format(value)

                    try:
                        is_valid = validator_func(value)
                    except Exception as other_exc:
                        msg += 'Exception: ' + str(other_exc)
                        is_valid = False

                if not is_valid:
                    exc = ValidationError(att_id, key, value, msg)
                    raise exc

                    # print('Invalid setting. Attribute: %r, Value: %r' % (key, value))
        super(AttrClass, self).__setattr__(key, value)
