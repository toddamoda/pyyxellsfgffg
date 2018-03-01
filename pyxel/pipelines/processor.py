"""TBW."""
import typing as t

from pyxel import util
from pyxel.detectors.ccd import CCD
from pyxel.detectors.cmos import CMOS
from pyxel.pipelines.ccd_pipeline import CCDDetectionPipeline
from pyxel.pipelines.cmos_pipeline import CMOSDetectionPipeline


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

    def __getstate__(self):
        """TBW."""
        return {
            'detector': self.detector,
            'pipeline': self.pipeline,
        }

    def set(self, key, value):
        """TBW.

        :param key:
        :param value:
        :return:
        """
        if value:
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
