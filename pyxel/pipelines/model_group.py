"""TBW."""
import logging
import typing as t  # noqa: F401

import esapy_config as om
from pyxel.pipelines.model_function import ModelFunction
from pyxel import util


class ModelGroup:
    """TBW."""

    def __init__(self, models: t.List[ModelFunction]) -> None:
        """TBW.

        :param models:
        """
        self.models = models    # type: t.List[ModelFunction]
        self._log = logging.getLogger(__name__)

    def get_state_json(self):
        """TBW."""
        return om.get_state_dict(self.models)

    def run(self, detector, pipeline):
        """Execute each enabled model in this group."""
        for model in self.models:
            if model.enabled:
                self._log.debug('Running %r', model.func)
                model.function(detector)
                if not pipeline.is_running:
                    self._log.debug('Aborted after %r', model.func)
                    raise util.PipelineAborted()
            else:
                pass

    def __getstate__(self):
        """TBW."""
        return {
            'models': self.models
        }

    def __getattr__(self, item):
        """TBW."""
        # if item == '__deepcopy__':
        #     return self.copy()
        if item == '__setstate__':
            return super().__getattr__(item)
        for model in self.models:         # THIS CAUSED AN INFINITE RECURSIVE LOOP, WHEN ModelGroup was deepcopied
            if model.name == item:
                return model

        # return super().__getattr__(item)
