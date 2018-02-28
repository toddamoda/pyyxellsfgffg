"""Utility functions."""

from pyxel.util.fitsfile import FitsFile


def update_fits_header(header, key, value):
    """TBW.

    :param header:
    :param key:
    :param value:
    :return:
    """
    if not isinstance(value, (str, int, float)):
        value = '%r' % value

    if isinstance(value, str):
        value = value[0:24]

    if isinstance(key, (list, tuple)):
        key = '/'.join(key)

    key = key.replace('.', '/')[0:36]

    header[key] = value


__all__ = ['FitsFile', 'update_fits_header']
