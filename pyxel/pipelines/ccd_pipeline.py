"""TBW."""
from pyxel.pipelines.detector_pipeline import DetectionPipeline
from pyxel.pipelines.model_group import ModelGroup


class CCDDetectionPipeline(DetectionPipeline):
    """TBW."""

    def __init__(self,
                 charge_transfer: ModelGroup = None,
                 **kwargs) -> None:
        """TBW.

        :param charge_transfer:
        :param kwargs:
        """
        super().__init__(**kwargs)
        self.charge_transfer = charge_transfer

        self._model_groups = ['photon_generation',
                              'optics',
                              'charge_generation',
                              'charge_collection',
                              'charge_transfer',
                              'charge_measurement',
                              'readout_electronics']

    def __getstate__(self):
        """TBW."""
        kwargs = super().__getstate__()
        kwargs_obj = {
            'charge_transfer': self.charge_transfer,
            '_model_groups': self.model_group_names,
        }
        return {**kwargs, **kwargs_obj}
