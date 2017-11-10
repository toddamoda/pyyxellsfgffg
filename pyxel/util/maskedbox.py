#   --------------------------------------------------------------------------
#   Copyright 2016 SRE-F, ESA (European Space Agency)
#       Hans Smit <Hans.Smit@esa.int>
#       Frederic Lemmel <Frederic.Lemmel@esa.int>
#   --------------------------------------------------------------------------
""" The MaskedBox class provides a set of convenience methods on an ndarray that enable a frame
sensor's image array to be sliced and masked.
"""

import numpy as np

from . import util


# class Threshold(object):
#     """ This class handles all image thresholding routines. Currently not used! """
#
#     def __init__(self, value_lo=None, value_hi=None,
#                  n_sigma=None, reference=None, noise=None,
#                  in_range=True):
#         """
#         :param float value_lo:
#         :param float value_hi:
#         :param float n_sigma:
#         :param float reference:
#         :param float noise:
#         :param bool in_range:
#         """
#         self.n_sigma = n_sigma
#         self.reference = reference
#         self.noise = noise
#         self.in_range = in_range
#         self._value_lo = value_lo
#         self._value_hi = value_hi
#
#     def __repr__(self):
#         dict_str = {key: repr(self.__dict__[key]) for key in self.__dict__}
#         args = '{_value_lo},{_value_hi},{n_sigma},{reference},{noise},{in_range}'
#         return 'Threshold(%s)' % args.format(**dict_str)
#
#     def apply_frame(self, frame, channel, offset=0):
#         """ Recalculate reference and offset values for the new frane and channel. """
#         offset_noise = frame.get_offset(channel)
#         offset += offset_noise
#         noise = frame.get_readout_noise(channel)
#         self.reference = offset
#         self.noise = noise
#
#     def _check(self):
#         """ Check if the attributes make sense, else raise a ValueError exception. """
#         if not isinstance(self.reference, (int, float)):
#             raise ValueError('threshold reference is not valid: %s' % repr(self.reference))
#         if not isinstance(self.noise, (int, float)):
#             raise ValueError('threshold noise is not valid: %s' % repr(self.noise))
#         if not isinstance(self.n_sigma, (int, float)):
#             raise ValueError('threshold n_sigma is not valid: %s' % repr(self.n_sigma))
#
#     @property
#     def value_lo(self):
#         """ Retrieve or calculate the low pixel value. """
#         if self._value_lo is not None:
#             return self._value_lo
#         else:
#             self._check()
#             return self.reference - (self.n_sigma * self.noise)
#
#     @property
#     def value_hi(self):
#         """ Retrieve or calculate the high pixel value. """
#         if self._value_hi is not None:
#             return self._value_hi
#         else:
#             self._check()
#             return self.reference + (self.n_sigma * self.noise)


class MaskedBox(object):
    """ This class overrides statistical numpy operations
    to handle image masks. When calculating the statistical operation
    only the masked pixel locations are taken into account.
    """

    def __init__(self, data, slice_rect=None):
        """
        :param ndarray data: channel frame image
        :param tuple slice_rect: (slice(y0, y1), slice(x0, x1))
        :raises TypeError: if the data argument is not a ndarray.
        """
        if not isinstance(data, np.ndarray):
            raise TypeError('Expected np.array, got: %s' % type(data))

        if data.ndim != 2:
            raise ValueError('Expected np.array to be of dimension 2, got: %s' % data.ndim)

        # always make a copy and ensure that it is a float
        # type (required for NaN masks)
        data = data.astype(float)

        if slice_rect is not None:
            data = data[slice_rect]
        else:
            slice_rect = (slice(0, data.shape[1]), slice(0, data.shape[0]))

        self.rect = slice_rect
        # self.frame = input_frame
        self._data = data
        self._mask = np.ones(self._data.shape).astype(bool)

    def reset(self):
        """ Reset the mask of this instance to no masking of pixels. """
        self._mask = np.ones(self._data.shape).astype(bool)

    @staticmethod
    def create_nan_mask(shape, mask_slices, bin_slices=1):
        """

        :param tuple shape:
        :param list mask_slices:
        :param int bin_slices:
        :return: NaN float array
        :rtype: ndarray
        :raises IndexError: if the masked slices are out of bounds.
        """
        mask = np.ones(shape, dtype=float)
        if isinstance(mask_slices, list):
            for y_x_slice in mask_slices:
                y_slice, x_slice = util.get_binned_slice(y_x_slice, bin_slices)
                try:
                    mask[y_slice, x_slice] = np.nan
                except IndexError as exc:
                    raise IndexError('Error during data masking operation. '
                                     'slice: %s, shape: %s, bins: %s, exc: %s'
                                     % (repr(y_x_slice), repr(shape), repr(bin_slices), str(exc)))
        return mask

    @staticmethod
    def to_nan_mask(mask):
        """
        :param ndarray mask:
        :return: new NaN float ndarray
        :rtype: ndarray
        """
        new_mask = mask.astype(bool).astype(float)
        new_mask[new_mask == 0.0] = np.NaN
        return new_mask

    @property
    def shape(self):
        """ Retrieve the sliced shape of the image array.

        :return: the 2d tuple, i.e. (height, width)
        :rtype: tuple
        """
        return self._data.shape

    @property
    def masked(self):
        """ Apply the mask transformation to the image data. The
        locations that are to be masked out will contain a NaN value.

        :return: the masked image data. The masked locations that
            are 0 or False will be set to NaN in the returned image.
        :rtype: ndarray
        """
        mask = self._mask.astype(float)
        mask[mask == 0.0] = np.NaN
        return self._data * mask

    @property
    def mask(self):
        """ Retrieve the mask for this object.

        :return: the boolean 2d masked array.
        :rtype: ndarray
        """
        return self._mask

    @mask.setter
    def mask(self, new_mask):
        """ Set a new mask for this object. The new_mask argument
        will be converted to a boolean ndarray, meaning, all 0's will
        be converted to False, and any other values to True.

        :param ndarray new_mask: the 2d ndarray.
        """
        # test if the new_mask is already a NaN array, if so, convert
        # the NaN to zeros
        if np.isnan(new_mask).any():
            new_mask = np.nan_to_num(new_mask)
        self._mask = new_mask.astype(bool)

    @property
    def data(self):
        """ Retrieve the image array.

        :return: the float typed image array as a sliced rectangle
            of the sensor frame.
        :rtype: ndarray
        """
        return self._data

    @data.setter
    def data(self, new_data):
        """ Set a new data array. It must be the same size and same type.

        :param ndarray new_data:
        """
        if not isinstance(new_data, np.ndarray):
            raise TypeError('Expected np.array, got: %s' % type(new_data))

        if new_data.ndim != 2:
            raise ValueError('Expected np.array to be of dimension 2, got: %s' % new_data.ndim)

        if self._data.dtype != new_data.dtype:
            raise TypeError('Expected similar type: %s , got: %s'
                            % (type(self._data.dtype), type(new_data)))
        self._data = new_data

    def get_threshold_mask(self, lo_val, hi_val, in_range=True):
        """
        :param float hi_val:
        :param float lo_val:
        :param bool in_range:
        :return: a new mask based on threshold values. The 2d array
            returned will be a boolean array.
        :rtype: ndarray
        """
        data = self._data
        if in_range:
            new_mask = np.logical_and(data > lo_val, data < hi_val)
        else:
            new_mask = np.logical_or(data < lo_val, data > hi_val)
        return new_mask

    def apply_threshold_mask(self, lo_val, hi_val, in_range=True):
        """
        :param float hi_val:
        :param float lo_val:
        :param bool in_range:
        """
        self._mask *= self.get_threshold_mask(lo_val, hi_val, in_range)

    def get_threshold_mask_n_sigma(self, n_sigma=1, reference=None, noise=None, in_range=True,
                                   axis=None):
        """
        :param int n_sigma:
        :param float reference:
        :param float noise:
        :param bool in_range:
        :param int axis:
        :return: the boolean mask 2d array
        :rtype: ndarray
        """
        if reference is None:
            reference = self.mean(axis)

        if noise is None:
            noise = self.std(axis)

        lo_val = (reference - (n_sigma * noise))
        hi_val = (reference + (n_sigma * noise))
        result = self.get_threshold_mask(lo_val, hi_val, in_range)
        return result

    def apply_threshold_mask_n_sigma(self, n_sigma=1, reference=None, noise=None, in_range=True,
                                     axis=None):
        """ Create a new mask based on threshold parameters.

        :param int n_sigma:
        :param float reference:
        :param float noise:
        :param bool in_range:
        :param int axis:
        """
        self._mask *= self.get_threshold_mask_n_sigma(n_sigma, reference, noise, in_range, axis)

    def sum(self, axis=None, dtype=None, out=None, keepdims=0):
        """ Convenience method to sum all pixels on the masked image array but leaving
        out the masked (NaN) pixels values.

        :param int axis: 0 is the y axis, 1 is the x-axis, None is both axis
        :param type dtype:
        :param ndarray out:
        :param int keepdims:
        :return: the sum of valid pixel values. If the axis parameter is set to 0 or 1,
            then a 1d ndarray is returned.
        :rtype: float
        """
        mask_data = self.masked
        return np.nansum(mask_data, axis, dtype, out, keepdims)

    def mean(self, axis=None, dtype=None, out=None, keepdims=False):
        """ Calculate the masked mean for this box'ed region on the
        sensor.

        :return: the mean (average) value
        :rtype: float
        """
        mask_data = self.masked
        if mask_data.size == 0:
            return np.nan
        result = np.nanmean(mask_data, axis, dtype, out, keepdims)
        return result

    def std(self, axis=None, dtype=None, out=None, ddof=0, keepdims=False):
        """ Calculate the masked standard deviation for this box'ed region
        on the sensor.

        :param int axis: Axis or axes along which the standard deviation is computed.
            The default is to compute the standard deviation of the flattened array.
            If this is a tuple of ints, a standard deviation is performed over
            multiple axes, instead of a single axis or all the axes as before.
        :param type dtype: Type to use in computing the standard deviation. For
            arrays of integer type the default is float64, for arrays of float
            types it is the same as the array type.
        :param ndarray out: Alternative output array in which to place the result.
            It must have the same shape as the expected output but the type
            (of the calculated values) will be cast if necessary.
        :param int ddof: degrees of freedom. For a 2d array this should
            be set to 1.
        :param bool keepdims: If this is set to True, the axes which are reduced are
            left in the result as dimensions with size one. With this option, the
            result will broadcast correctly against the original arr.
        :return: the standard deviation value
        :rtype: float
        """
        mask_data = self.masked
        if mask_data.size == 0:
            return np.nan
        result = np.nanstd(mask_data, axis, dtype, out, ddof, keepdims)
        return result

    def median(self):
        """ Calculate the masked median for this box'ed region on the
        sensor.

        :return: the median value
        :rtype: float
        """
        mask_data = self.masked
        if mask_data.size == 0:
            return np.nan
        result = np.nanmedian(mask_data)
        return result

    def flatten(self, replace_nan_with=None, order='C'):
        """ Convert 2d to 1d array according to specify order and if remove_nan strip out the
        masked locations. This can then be used to do analysis with. Example, mean and std.

        :param float replace_nan_with: if set to None then the NaN's encountered are removed, else
            the NaN's are replaced with the float value specified.
        :param str order: the order in which the array is converted from 2D to 1D (see numpy
            flatten documentation). Allowed values: 'C', 'F', 'A'
        :return: the 1d array of masked pixel values.
        :rtype: 1d ndrarray
        """
        mask_data = self.masked
        mask_data = mask_data.flatten(order)  # nan's are in this array
        if replace_nan_with is None:
            mask_data = mask_data[~np.isnan(mask_data)]

        elif replace_nan_with == 0.0:
            mask_data = np.nan_to_num(mask_data)  # replaces with 0.0

        elif not np.isnan(replace_nan_with):
            mask_data = np.where(np.isnan(mask_data), replace_nan_with, mask_data)

        return mask_data

        # if order is not 'C':
        #
        # if replace_nan_with is None:
        #     result = mask_data[~np.isnan(mask_data)]
        # elif mask_data.ndim > 1:
        #     result = mask_data.flatten(order)
        # else:
        #     result = mask_data
        # return result
