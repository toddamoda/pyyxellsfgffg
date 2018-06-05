"""TBW."""
import esapy_config as om

from pyxel.detectors.geometry import Geometry

# import os
import numpy as np
from esapy_sensor.sensor_ccd import CCDSensorGeometry, CCDFrame, HeaderPLATO


@om.attr_class
class CCDGeometry(Geometry):
    """TBW."""

    def copy(self):
        """TBW."""
        return CCDGeometry(**self.__getstate__())

    def __getstate__(self):
        """TBW."""
        states = super().__getstate__()
        ccd_states = {
            # add specific CCD attributes here
        }
        return {**states, **ccd_states}

    def create_sensor(self):
        """Construct esapy_sensor objects for CCD geometry and frame

        :return:
        """
        # # self.row = 10
        # # self.col = 16

        # p_over_scan = 3
        # s_over_scan = 4

        # self.sensor_geometry = CCDSensorGeometry(
        #     channels_layout=(1, 1),  # row, cols
        #     readout_direction=True,
        #     p_pre_scan_y=2,
        #     s_pre_scan_x=2,
        #     active_y=5,     # image area rows  -> # p_over_scan = 3
        #     active_x=10,    # image area cols  -> # s_over_scan = 4
        #     masked_slices=None)
        #
        # # CWD_DIR = os.path.dirname(os.path.realpath(__file__))
        # # fits_file = os.path.join(CWD_DIR, '../../data/test_1.fits')
        # # frame = sensor_ccd.CCDFrame(fits_file, sensor_ccd.HeaderPLATO, geo)
        #
        # self.frame = CCDFrame(np.zeros((self.row, self.col), dtype=int), HeaderPLATO, self.sensor_geometry)
        #
        # print(self.frame.data[self.frame.roi.active])
        # # self.frame.data[self.frame.roi.s_over_scan]
        # # self.frame.data[self.frame.roi.p_over_scan]
        #
        # # define an optional ROI (in arbritrary number):
        # x0 = 1
        # y0 = 3
        # x1 = 1
        # y1 = 3
        # self.frame.add_roi('roi_name', (x0, y0, x1, y1))
        # # TODO for what we need these rois? for models?
        # # self.frame.data[self.frame.roi.roi_name]
        #
        #
        # # self.frame
        # # frame.roi
        # # frame.channels
        # # frame.get_data(0)
        # # frame.get_data(1)
        # # frame.data
        # # frame.get_stats(0)
        # # frame.get_stats(1)
        # #
        # # # frame.get_offset(0)
        # # # frame.get_readout_noise(1)
        #
        # # mask = frame.box(0, (x0, y0, x1, y1))
        # # mask.data
        # # mask.shape
        # # frame.set_user_defined_roi()
        #
        # print('a')
