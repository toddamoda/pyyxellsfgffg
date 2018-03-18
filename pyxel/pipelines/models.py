"""TBW."""
import logging
import functools
import typing as t  # noqa: F401
from pyxel import util
from pyxel.util import objmod as om


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
        return Model(**om.copy_state(self))

    def get_state_json(self):
        """TBW."""
        return om.get_state_dict(self)

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
        func_ref = om.evaluate_reference(self.name)
        func = functools.partial(func_ref, **self.arguments)
        return func


class Models:
    """TBW."""

    def __init__(self, models: t.Dict[str, Model]) -> None:
        """TBW.

        :param models:
        """
        self.models = models    # type: t.Dict[str, Model]
        self._log = logging.getLogger(__name__)

    def copy(self):
        """TBW."""
        models = {key: model.copy() for key, model in self.models.items()}
        return Models(models=models)

    def get_state_json(self):
        """TBW."""
        return om.get_state_dict(self)

    def run(self, detector, pipeline):
        """Execute each enabled model in this group."""
        groups = pipeline.model_groups
        model_keys = dict(zip(groups.values(), groups.keys()))  # switch key/values
        key = model_keys[self]  # retrieve group name
        for step in getattr(pipeline, '_model_steps')[key]:  # deprecated attribute
            if step in self.models:
                model = self.models[step]  # type: Model
                if model.enabled:
                    self._log.debug('Running %r', model.name)
                    for arg in model.arguments:
                        util.update_fits_header(detector.header,
                                                key=[step, arg],
                                                value=model.arguments[arg])
                    model.function(detector)
                    if not pipeline.is_running:
                        self._log.debug('Aborted after %r', model.name)
                        raise util.PipelineAborted()
                else:
                    self._log.debug('Skipping %r', model.name)

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
