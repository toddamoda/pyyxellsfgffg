"""TBW."""
import logging
import functools
import typing as t  # noqa: F401

from pyxel import util
# from pyxel.detectors.detector import Detector


class ModelFunction:
    """TBW."""

    def __init__(self, name: str, func, arguments: dict = None, enabled: bool = True) -> None:
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

    def copy(self):
        """TBW."""
        # kwargs = {key: type(value)(value) for key, value in self.__getstate__().items()}
        return ModelFunction(**util.copy_state(self))

    def get_state_json(self):
        """TBW."""
        return util.get_state_dict(self)

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
        func_ref = util.evaluate_reference(self.func)
        if isinstance(func_ref, type):
            # this is a class type, instantiate it using default arguments.
            func_ref = func_ref()
        func = functools.partial(func_ref, **self.arguments)
        return func


class ModelGroup:
    """TBW."""

    def __init__(self, models: t.List[ModelFunction]) -> None:
        """TBW.

        :param models:
        """
        self.models = models    # type: t.List[ModelFunction]
        self._log = logging.getLogger(__name__)

    def copy(self):
        """TBW."""
        models = {key: model.copy() for key, model in self.models.items()}
        return ModelGroup(models=models)

    def get_state_json(self):
        """TBW."""
        # return util.get_state_dict(self)
        return {model.name: util.get_state_dict(model) for model in self.models}

    def run(self, detector, pipeline):
        """Execute each enabled model in this group."""
        for model in self.models:
            if model.enabled:
                self._log.debug('Running %r', model.func)
                for arg in model.arguments:
                    util.update_fits_header(detector.header,
                                            key=[model.name, arg],
                                            value=model.arguments[arg])
                model.function(detector)
                if not pipeline.is_running:
                    self._log.debug('Aborted after %r', model.func)
                    raise util.PipelineAborted()
            else:
                self._log.debug('Skipping %r', model.func)

    def __getstate__(self):
        """TBW."""
        return {
            'models': self.models
        }

    def __getattr__(self, item):
        """TBW."""
        for model in self.models:
            if model.name == item:
                return model

        return super().__getattr__(item)
