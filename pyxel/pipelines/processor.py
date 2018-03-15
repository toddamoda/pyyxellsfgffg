"""TBW."""
import typing as t

from pyxel import util
from pyxel.detectors.ccd import CCD
from pyxel.detectors.cmos import CMOS
from pyxel.pipelines.ccd_pipeline import CCDDetectionPipeline
from pyxel.pipelines.cmos_pipeline import CMOSDetectionPipeline
from pyxel.pipelines import validator


class Processor:
    """TBW."""

    def __init__(self,
                 detector: t.Union[CCD, CMOS],
                 pipeline: t.Union[CCDDetectionPipeline, CMOSDetectionPipeline]) -> None:
        """TBW.

        :param detector:
        :param pipeline:
        """
        self.detector = detector
        self.pipeline = pipeline

    def copy(self):
        """TBW."""
        return Processor(self.detector.copy(), self.pipeline.copy())

    def get_state_json(self):
        """TBW."""
        return util.get_state_dict(self)

    def __getstate__(self):
        """TBW."""
        return {
            'detector': self.detector,
            'pipeline': self.pipeline,
        }

    def validate(self):
        """TBW."""
        errors = []
        for key, model_group in self.pipeline.model_groups.items():
            for model in model_group.models:
                if model.enabled:
                    errors += validator.validate_call(model.func, False, kwargs=model.arguments)
        return errors

    def has(self, key):
        """TBW.

        :param key:
        :return:
        """
        found = False
        obj, att = util.get_obj_att(self, key)
        if isinstance(obj, dict) and att in obj:
            found = True
        elif hasattr(obj, att):
            found = True
        return found

    def get(self, key):
        """TBW.

        :param key:
        :return:
        """
        return util.get_value(self, key)

    def set(self, key, value, convert_value=True):
        """TBW.

        :param key:
        :param value:
        :param convert_value:
        :return:
        """
        if convert_value and value:
            # convert the string based value to a number
            if isinstance(value, list):
                for i, val in enumerate(value):
                    if val:
                        value[i] = util.eval_entry(val)
            else:
                value = util.eval_entry(value)

        obj, att = util.get_obj_att(self, key)

        if isinstance(obj, dict) and att in obj:
            obj[att] = value
        else:
            setattr(obj, att, value)
