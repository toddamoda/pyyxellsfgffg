"""TBW."""
import functools
import typing as t  # noqa: F401
from pyxel import util


class Model:
    """TBW."""

    def __init__(self, name: str, arguments: dict = None, enabled: bool = True) -> None:
        """TBW.

        :param name:
        :param enabled:
        :param arguments:
        """
        if arguments is None:
            arguments = {}
        self.name = name
        self.enabled = enabled
        self.arguments = arguments

    def copy(self):
        """TBW."""
        # kwargs = {key: type(value)(value) for key, value in self.__getstate__().items()}
        return Model(**util.copy_state(self))

    def get_state_json(self):
        """TBW."""
        return util.get_state_dict(self)

    def __getstate__(self):
        """TBW."""
        return {
            'name': self.name,
            'enabled': self.enabled,
            'arguments': self.arguments
        }

    @property
    def function(self):
        """TBW."""
        func_ref = util.evaluate_reference(self.name)
        func = functools.partial(func_ref, **self.arguments)
        return func


class Models:
    """TBW."""

    def __init__(self, models: t.Dict[str, Model]) -> None:
        """TBW.

        :param models:
        """
        self.models = models    # type: t.Dict[str, Model]

    def copy(self):
        """TBW."""
        models = {key: model.copy() for key, model in self.models.items()}
        return Models(models=models)

    def get_state_json(self):
        """TBW."""
        return util.get_state_dict(self)

    def __getstate__(self):
        """TBW."""
        return {
            'models': self.models
        }

    def __getattr__(self, item):
        """TBW."""
        if item in self.models:
            return self.models[item]
        return super().__getattr__(item)
