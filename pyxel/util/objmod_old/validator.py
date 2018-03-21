"""TBW."""


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
        msg = 'Validation failed: %(func)r, arg: %(arg)r, value: %(value)r, msg: %(msg)r'
        msg = msg % vars(self)
        return msg


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


def check_range(min_val, max_val, step=None, enforce_step=True):
    """TBW.

    :param min_val:
    :param max_val:
    :param step:
    :param enforce_step:
    """
    def _wrapper(value):
        """TBW."""
        # Do something
        result = False
        if min_val <= value <= max_val:
            result = True
            if step and enforce_step:
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
        'min_val': min_val, 'max_val': max_val, 'step': step, 'enforce_step': enforce_step
    }
    setattr(_wrapper, 'validate_info', info)

    return _wrapper
