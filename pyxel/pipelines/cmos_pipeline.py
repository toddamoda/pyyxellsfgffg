"""TBW."""
# from pyxel.pipelines.pipeline import DetectionPipeline
# from pyxel.pipelines.model_group import ModelGroup
#
#
# class CMOSDetectionPipeline(DetectionPipeline):
#     """TBW."""
#
#     def __init__(self,
#                  signal_transfer: ModelGroup = None,
#                  **kwargs) -> None:
#         """TBW.
#
#         :param signal_transfer:
#         :param kwargs:
#         """
#         super().__init__(**kwargs)
#         self.signal_transfer = signal_transfer
#
#         self._model_groups = ['photon_generation',
#                               'optics',
#                               'charge_generation',
#                               'charge_collection',
#                               'charge_measurement',
#                               'signal_transfer',
#                               'readout_electronics']
#
#     def __getstate__(self):
#         """TBW."""
#         kwargs = super().__getstate__()
#         kwargs_obj = {
#             'signal_transfer': self.signal_transfer,
#             '_model_groups': self.model_group_names,
#         }
#         return {**kwargs, **kwargs_obj}
