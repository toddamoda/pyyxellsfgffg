"""TBW."""
import functools
import esapy_config as om


class ModelFunction:
    """TBW."""

    def __init__(self,
                 func,  # callable or str
                 name: str = None,
                 arguments: dict = None,
                 enabled: bool = True) -> None:
        """TBW.

        :param name:
        :param enabled:
        :param arguments:
        """
        if callable(func):
            func = func.__module__ + '.' + func.__name__

        if arguments is None:
            arguments = {}
        self.func = func
        self.name = name
        self.enabled = enabled
        self.arguments = arguments
        # self.group = None               # TODO

    def __repr__(self):
        """TBW."""
        return 'ModelFunction(%(name)r, %(func)r, %(arguments)r, %(enabled)r)' % vars(self)

    def get_state_json(self):
        """TBW."""
        return om.get_state_dict(self)

    def __getstate__(self):
        """TBW."""
        return {
            'name': self.name,
            'func': self.func,
            'enabled': self.enabled,
            'arguments': self.arguments
        }

    @property
    def function(self):
        """TBW."""
        func_ref = om.evaluate_reference(self.func)
        if isinstance(func_ref, type):
            # this is a class type, instantiate it using default arguments.
            func_ref = func_ref()
        func = functools.partial(func_ref, **self.arguments)
        return func
