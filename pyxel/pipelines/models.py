import typing as t  # noqa: F401
from pyxel.util import util


class Models:

    def __init__(self, models: dict) -> None:

        new_dct = {}
        for key, value in models.items():

            if isinstance(value, str):
                func = util.evaluate_reference(value)  # type: t.Callable

            elif callable(value):
                func = value

            else:
                raise NotImplementedError('Model defined in config file is not implemented yet')

            new_dct[key] = func

        self.models = new_dct                   # type: t.Dict[str, t.Callable]
