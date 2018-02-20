#   --------------------------------------------------------------------------
#   Copyright 2016 SRE-F, ESA (European Space Agency)
#       Thibaut Prodhomme <thibaut.prodhomme@esa.int>
#       Hans Smit <Hans.Smit@esa.int>
#       Frederic Lemmel <Frederic.Lemmel@esa.int>
#   --------------------------------------------------------------------------
# pylint: disable=missing-docstring

"""This module defines the CCD sensor types and the various regions of the sensor area."""

from collections import OrderedDict

import numpy as np

from . import util
from .maskedbox import MaskedBox
from .fitsfile import FitsFile
from .fitsfile import HeaderAccess
from .fitsfile import ImageData


class SensorException(Exception):
    """All exception in this module should inherit from this class."""


class ChannelConfig(object):
    """Abstract class that defines the layout of a channel."""


class SensorGeometry(object):
    """Abstract class that defines the sensor invariants related to geometry."""


class SensorHeader(HeaderAccess):
    """This class defines the required FITS header keys and type information.

    This is to be sub-classed for each different test bench.
    """

    gain = (None, float)
    post_int_time = (None, float)
    int_time = (None, float)
    pre_int_time = (None, float)
    bins = (None, int)
    temperature = (None, float)
    acq_index = (None, int)
    acq_length = (None, int)
    n_rows = (None, int)
    n_cols = (None, int)
    wave_len = (None, float)
    sw_version = (None, str)
    file_name = (None, str)
    injections = (None, int)
    no_injections = (None, int)
    blocks = (None, int)
    rd = (None, float)
    od = (None, float)
    gd = (None, float)
    date = (None, str)
    pt = (None, int)
    ser_pump_delay = (None, int)

    # TODO: add method to access fits header directly, i.e. PARAM2


# class HeaderPLATO(SensorHeader):
#     """ FITS key header mapping """
#
#     gain = ('GAIN', float, 1.0)
#     pre_int_time = ('PRETIME', float, 0.0)
#     int_time = ('INTTIME', float, 0.0)
#     post_int_time = ('POSTTIME', float, 0.0)
#     bins = ('BINROW', int, 1)
#     temperature = ('SENSOR11', float, 180.0)
#     acq_index = ('ACQ_IDX', int, 1)
#     acq_length = ('ACQ_LEN', int, 1)
#     n_rows = ('NAXIS2', int, 100)
#     n_cols = ('NAXIS1', int, 100)
#     wave_len = ('WAVELEN', float, 0.0)
#     sw_version = ('SW_VERSI', str, '')
#     file_name = ('FILENAME', str, '')
#     injections = ('PARAM16', int, 100)
#     no_injections = ('PARAM17', int, 100)
#     blocks = ('PARAM18', int, 100)
#     rd = ('HV_RDE', float, 0.00)
#     od = ('HV_ODE', float, 0.00)
#     gd = ('HV_GD', float, 0.00)
#     date = ('DATE', str, '')
#     pt = ('PARAM11', int, 100)
#     ser_pump_delay = ('PARAM19', int, 100)


class CCDSensorGeometry(SensorGeometry):
    """This class contains the CCD sensor invariants related to channel layout and geometry.

    It also includes several convenience methods.

    """

    def __init__(self,
                 channels_layout,
                 readout_direction,
                 p_pre_scan_y,
                 s_pre_scan_x,
                 active_y,
                 active_x,
                 masked_slices=None,
                 **_kwargs):
        """TBW.

        :param tuple channels_layout: (rows, cols) tuple of channels
        :param list readout_direction: serial readout direction per channel
        :param int p_pre_scan_y: number of pixels of parallel pre-scan
        :param int s_pre_scan_x: number of pixels of serial pre-scan
        :param int active_y: the total number of active pixels for the entire
            sensor in the parallel direction (y)
        :param int active_x: the total number of active pixels for the entire
            sensor in the serial direction (x)
        :param list masked_slices:
        :param dict _kwargs: unused. This is added for convenience when constructing
            an instance of this class from a configuration file.
        """
        self.channels_layout = channels_layout  # example: (1, 2) => rows, cols
        self.readout_direction = readout_direction  # example: True <-, False ->
        self.p_pre_scan_y = p_pre_scan_y  # example 0 pixels
        self.s_pre_scan_x = s_pre_scan_x
        self.active_shape = (active_y, active_x)  # total number of active pixels on sensor

        if masked_slices is None:
            self.masked_slices = []
        else:
            self.masked_slices = masked_slices

        if isinstance(readout_direction, (tuple, list)):
            self.readout_direction = readout_direction
        else:
            channels = self.channels_layout[1] * self.channels_layout[0]
            self.readout_direction = [readout_direction] * channels

    @property
    def channel_active_shape(self):
        """TBW.

        :return:
        """
        return (self.active_shape[0] // self.channels_layout[0],
                self.active_shape[1] // self.channels_layout[1])


def x_shifter(channels):
    """TBW.

    :param channels:
    :return:
    """
    return lambda data, ch_count=channels: np.roll(data, -data.shape[1] // ch_count)


class CCDChannelConfig(ChannelConfig):
    """TBW."""

    channel_transformations = {
        (1, 1): [[]],
        (1, 2): [[], [np.fliplr]],
        (2, 1): [[], [np.flipud]],
        (1, 4): [[], [x_shifter(4)], [np.fliplr, x_shifter(4)], [np.fliplr]],
        (2, 2): [[], [np.fliplr], [np.fliplr, np.flipud], [np.flipud]],
    }

    def __init__(self, sensor_geometry, image_shape, binned_rows=1):
        """TBW.

        :param CCDSensorGeometry sensor_geometry:
        :param tuple image_shape:
        :param int binned_rows:
        """
        super(CCDChannelConfig, self).__init__()

        self._geometry = sensor_geometry
        self._image_shape = image_shape
        self._binned_rows = binned_rows

    def get_channel_data(self, channel, image):
        """TBW.

        :param int channel:
        :param ndarray image:
        :return: the masked and transformed channel data
        :rtype: ndarray
        """
        # apply the global frame mask on the entire image
        mask = MaskedBox.create_nan_mask(self._image_shape,
                                         self._geometry.masked_slices,
                                         self._binned_rows)
        data = image.astype(float) * mask

        # translate the Nth channel to channel 0
        ops = self.channel_transformations[self._geometry.channels_layout]
        for operation in ops[channel]:
            data = operation(data)

        # extract the channel data
        data = data[0:self.channel_height, 0:self.channel_width]

        # flip the channel data if the serial readout direction is reversed.
        if not self._geometry.readout_direction[channel]:
            data = np.fliplr(data)

        return data

    # @property
    # def channels_layout(self):
    #     return self._geometry.channels_layout

    @property
    def p_pre_scan_y(self):
        """TBW.

        :return:
        """
        return self._geometry.p_pre_scan_y

    @property
    def s_pre_scan_x(self):
        """TBW.

        :return:
        """
        return self._geometry.s_pre_scan_x

    @property
    def channel_active_shape(self):
        """TBW.

        :return:
        """
        return self._geometry.channel_active_shape

    @property
    def image_shape(self):
        """TBW.

        :return:
        """
        return self._image_shape

    @property
    def channel_width(self):
        """TBW.

        :return:
        """
        return self._image_shape[1] // self._geometry.channels_layout[1]

    @property
    def channel_height(self):
        """TBW.

        :return:
        """
        return self._image_shape[0] // self._geometry.channels_layout[0]

    @property
    def channel_shape(self):
        """TBW.

        :return:
        """
        return (self._image_shape[0] // self._geometry.channels_layout[0],
                self._image_shape[1] // self._geometry.channels_layout[1])

    @property
    def p_over_scan_y(self):
        """TBW.

        :return:
        """
        # p_over_scan = height - active_y - p_pre_scan_y
        ch_total = self._image_shape[0] // self._geometry.channels_layout[0]
        ch_active = self._geometry.active_shape[0] // self._geometry.channels_layout[0]
        ch_pre_scan = self._geometry.p_pre_scan_y

        result = ch_total - ch_active - ch_pre_scan
        return max(result, 0)

    @property
    def s_over_scan_x(self):
        """TBW."""
        # s_over_scan = width - active_x - s_pre_scan_y.
        ch_total = self._image_shape[1] // self._geometry.channels_layout[1]
        ch_active = self._geometry.active_shape[1] // self._geometry.channels_layout[1]
        ch_pre_scan = self._geometry.s_pre_scan_x

        result = ch_total - ch_active - ch_pre_scan
        return max(result, 0)


class SensorFrame(object):
    """Generic Image Frame."""

    def __init__(self, fits_file, header_class, geometry, roi_class, channel_config_type):
        """TBW.

        :param fits_file:
        :param header_class:
        :param geometry:
        :param roi_class:
        :param channel_config_type:
        """
        super(SensorFrame, self).__init__()

        if isinstance(fits_file, np.ndarray):
            fits_file = ImageData(fits_file)
        elif isinstance(fits_file, str):
            fits_file = FitsFile(fits_file)

        self._fits = fits_file
        self._geometry = geometry

        self._roi_object = None
        self._roi_class = roi_class

        self._header_object = None
        self._header_class = header_class

        self._channel_object = None
        self._channel_class = channel_config_type

    def load(self, fits_file=None):
        """Force the data and header to be loaded into memory.

        :param str fits_file: optionally load a different file
        """
        if fits_file is not None:
            if str(self._fits.filename) != fits_file:
                self._fits = FitsFile(fits_file)

        if not self._fits.is_loaded():
            self._fits.load()

    @property
    def roi(self):
        """TBW.

        :return:
        """
        if self._channel_object is None:
            self._channel_object = self._channel_class(self._geometry, self.data.shape, self.param.bins)

        if self._roi_object is None:
            self._roi_object = self._roi_class(self._channel_object)
        return self._roi_object

    # @roi.setter
    # def roi(self, roi_class):
    #     if self._channel_object is None:
    #         self._channel_object = self._channel_class(self._geometry, self.data.shape, self.param.bins)
    #
    #     self._roi_class = roi_class
    #     self._roi_object = self._roi_class(self._channel_object)
    #     return self._roi_object

    @property
    def filename(self):
        """TBW.

        :return:
        """
        if isinstance(self._fits, FitsFile):
            return self._fits.filename

    @property
    def channels(self):
        """TBW.

        :return:
        """
        return self._geometry.channels_layout[0] * self._geometry.channels_layout[1]

    @property
    def param(self):
        """TBW.

        :return:
        """
        if self._header_object is None:
            self._header_object = self._header_class.to_object(self.header)
        return self._header_object

    @property
    def header(self):
        """TBW.

        :return:
        """
        return self._fits.header

    @property
    def data(self):
        """TBW.

        :return:
        """
        return self._fits.data

    def get_data(self, channel):
        """Retrieve the sub-image for the corresponding channel.

        :param int channel:
        :return: image array for specified channel
        """
        full_image = self.data
        if self._channel_object is None:
            self._channel_object = self._channel_class(self._geometry, full_image.shape, self.param.bins)

        ch_image = self._channel_object.get_channel_data(channel, full_image)
        return ch_image

    def box(self, channel, rect):
        """Construct a new channel masked slice of the image using this factory method.

        :return: 2d ndarray
        :rtype: MaskedBox
        """
        data = self.get_data(channel)
        y_x_slice = util.rect_to_slice(rect)
        y_x_slice = util.get_binned_slice(y_x_slice, self.param.bins)
        return MaskedBox(data, y_x_slice)

    def set_user_defined_roi(self, y_0, y_1, x_0, x_1):
        """TBW.

        :param y_0:
        :param y_1:
        :param x_0:
        :param x_1:
        :return:
        """
        self.add_roi('user_defined', [y_0, y_1, x_0, x_1])

    def add_roi(self, name, rect):
        """TBW.

        :param name:
        :param rect:
        :return:
        """
        y_x_slice = util.rect_to_slice(rect)
        setattr(self.roi, name, y_x_slice)

    @property
    def roi_dict(self):
        """TBW.

        :return:
        """
        result = {}
        for name in self.roi.__dict__:
            att = self.roi.__dict__[name]
            is_slice = []
            if isinstance(att, tuple):
                is_slice = [isinstance(part, slice) for part in att]
            if len(is_slice) and False not in is_slice:
                result[name] = att
        return result

    # def get_roi_names(self):
    #     names = []
    #     for name in self.roi.__dict__:
    #         att = self.roi.__dict__[name]
    #         is_slice = []
    #         if isinstance(att, tuple):
    #             is_slice = [isinstance(part, slice) for part in att]
    #         if len(is_slice) and False not in is_slice:
    #             names.append(name)
    #     return names
    #
    # def get_roi_list(self):
    #     rois = self.get_roi_names()
    #     result = []
    #     for roi in rois:
    #         roi_slice = getattr(self.roi, roi)
    #         result.append(roi_slice)
    #     return result

    def get_stats(self, channel):
        """TBW."""
        result = OrderedDict()
        for name in self.roi_dict:
            box = self.box(channel, self.roi_dict[name])
            result[name] = (box.mean(), box.std())
        return result

    @staticmethod
    def construct(
            data,
            sensor_type,
            header_type,
            geometry_config):
        """TBW.

        :param str data: may be a file or a ndarray
        :param str sensor_type:
        :param str header_type:
        :param dict geometry_config:
        :return: a SensorFrame sub class instance
        :rtype: SensorFrame
        :raises TypeError: if any of the arguments passed have an incorrect type.
        """
        if isinstance(header_type, str):
            header_type = util.evaluate_reference(header_type)

        if isinstance(sensor_type, str):
            sensor_type = util.evaluate_reference(sensor_type)

        header = header_type()

        if isinstance(data, np.ndarray):
            bins_name = header.bins[0]
            data = ImageData(data, header={bins_name: 1})
        elif isinstance(data, str):
            data = FitsFile(data)

        if isinstance(geometry_config, dict):
            args = util.get_missing_arguments(sensor_type.geometry_type.__init__, geometry_config)
            if len(args):
                raise TypeError('Missing SensorGeometry argument(s): %s' % repr(args))
            geometry_config = sensor_type.geometry_type(**geometry_config)

        if not isinstance(geometry_config, SensorGeometry):
            raise TypeError('Could not construct a SensorGeometry instance.')

        if not isinstance(data, ImageData):
            raise TypeError('Could not construct a ImageData instance.')

        if not isinstance(header, SensorHeader):
            raise TypeError('Could not construct a SensorHeader instance.')

        sensor_obj = sensor_type(data, header, geometry_config)
        return sensor_obj


class CCDFrame(SensorFrame):
    """Generic E2V CCD sensor methods are defined in this class.

    .. TODO: rename to CCD since all CCD's have the same region names
    """

    geometry_type = CCDSensorGeometry

    class ROI(object):
        """Region of interest slice coordinates for channel 0."""

        def __init__(self, ch_cfg):
            """TBW.

            :param ch_cfg:
            """
            # TODO: s_pre_scan_x should be configurable per channel and passed as an array
            self.active = (
                slice(ch_cfg.p_pre_scan_y, ch_cfg.channel_height - ch_cfg.p_over_scan_y),
                slice(ch_cfg.s_pre_scan_x, ch_cfg.channel_width - ch_cfg.s_over_scan_x)
            )
            self.sp_over_scan = (
                slice(ch_cfg.channel_height - ch_cfg.p_over_scan_y, ch_cfg.channel_height),
                slice(ch_cfg.channel_width - ch_cfg.s_over_scan_x, ch_cfg.channel_width)
            )
            self.s_pre_scan = (
                slice(0, ch_cfg.channel_height),
                slice(0, ch_cfg.s_pre_scan_x)
            )
            self.s_over_scan = (
                slice(0, ch_cfg.channel_height),
                slice(ch_cfg.channel_width - ch_cfg.s_over_scan_x, ch_cfg.channel_width)
            )
            self.p_pre_scan = (
                slice(0, ch_cfg.p_pre_scan_y),
                slice(0, ch_cfg.channel_width)
            )
            self.p_over_scan = (
                slice(ch_cfg.channel_height - ch_cfg.p_over_scan_y, ch_cfg.channel_height),
                slice(0, ch_cfg.channel_width)
            )

    def get_readout_noise(self, output_idx=0, gain=1.0):
        """Return the readout noise of the image.

        :param int output_idx: channel index number 0 - 3
        :param float gain: the gain setting
        :return: the standard deviation value of the  parallel + serial over-scan area
        :rtype: float
        :raises ValueError: is raised if the channel output is out of range.
        """
        if 0 <= output_idx < self.channels:
            data = self.box(output_idx, self.roi.sp_over_scan)
            return float(gain * data.std())
        raise ValueError('output_idx is out of range: %d' % output_idx)

    def get_offset(self, output_idx=0):
        """Return the electronic offset mean value.

        :param int output_idx: channel index number 0 - 3
        :return: the mean value of the parallel + serial over-scan area
        :rtype: float
        :raises ValueError: is raised if the channel output is out of range.
        """
        if 0 <= output_idx < self.channels:
            data = self.box(output_idx, self.roi.sp_over_scan)
            return float(data.mean())
        raise ValueError('output_idx is out of range: %d' % output_idx)

    def __init__(self, fits_file, header_keys, geometry):
        """TBW.

        :param fits_file:
        :param header_keys:
        :param geometry:
        """
        super(CCDFrame, self).__init__(fits_file,
                                       header_keys,
                                       geometry,
                                       CCDFrame.ROI,
                                       CCDChannelConfig)
