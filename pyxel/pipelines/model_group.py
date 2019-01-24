"""TBW."""
import typing as t  # noqa: F401
from pyxel.pipelines.model_function import ModelFunction
from pyxel import util


class ModelGroup:
    """TBW."""

    def __init__(self, models: t.List[ModelFunction]) -> None:
        """TBW.

        :param models:
        """
        self.models = models    # type: t.List[ModelFunction]

    def run(self, detector, pipeline, abort_model: str = None):
        """Execute each enabled model in this group."""
        for model in self.models:
            if model.name == abort_model:
                return True
            if not pipeline.is_running:
                raise util.PipelineAborted('Pipeline has been aborted.')
            else:
                if model.enabled:
                    model.function(detector)
        return False

    def __getstate__(self):
        """TBW."""
        return {'models': self.models}

    def __setstate__(self, item):
        """TBW."""
        self.models = item['models']

    def __getattr__(self, item):
        """TBW."""
        for model in self.models:
            if model.name == item:
                return model
