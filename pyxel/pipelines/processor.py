"""TBW."""
import typing as t

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
