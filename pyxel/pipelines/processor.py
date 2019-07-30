"""TBW."""
import typing as t
from esapy_config import get_obj_att, eval_entry, get_value
from pyxel.detectors.ccd import CCD
from pyxel.detectors.cmos import CMOS
from pyxel.pipelines.pipeline import DetectionPipeline


class Processor:
    """TBW."""

    def __init__(self,
                 detector: t.Union[CCD, CMOS],
                 pipeline: DetectionPipeline) -> None:
        """TBW.

        :param detector:
        :param pipeline:
        """
        self.detector = detector
        self.pipeline = pipeline

    def has(self, key):
        """TBW.

        :param key:
        :return:
        """
        found = False
        obj, att = get_obj_att(self, key)
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
        return get_value(self, key)

    def set(self, key, value, convert_value=True):
        """TBW.

        :param key:
        :param value:
        :param convert_value:
        :return:
        """
        if convert_value:  # and value:
            # convert the string based value to a number
            if isinstance(value, list):
                for i, val in enumerate(value):
                    if val:
                        value[i] = eval_entry(val)
            else:
                value = eval_entry(value)

        obj, att = get_obj_att(self, key)

        if isinstance(obj, dict) and att in obj:
            obj[att] = value
        else:
            setattr(obj, att, value)

    def run_pipeline(self, abort_before: str = None):
        """TBW.

        :param abort_before: str, model name, the pipeline should be aborted before this
        :return:
        """
        self.pipeline._is_running = True
        for group_name in self.pipeline.model_group_names:
            models_grp = getattr(self.pipeline, group_name)
            if models_grp:
                abort_flag = models_grp.run(self.detector, self.pipeline, abort_model=abort_before)
                if abort_flag:
                    break
        self.pipeline._is_running = False
        return self
