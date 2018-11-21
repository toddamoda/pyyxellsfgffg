#   --------------------------------------------------------------------------
#   Copyright 2016 SCI-FIV, ESA (European Space Agency)
#       Hans Smit <Hans.Smit@esa.int>
#       Frederic Lemmel <Frederic.Lemmel@esa.int>
#   --------------------------------------------------------------------------
"""Class to access 'data' and 'header' from a FITS file."""

import logging
import sys
import os
import glob
import inspect

from astropy.io import fits as pyfits

try:
    from pathlib2 import Path  # needed for anaconda on Mac
except ImportError:
    Path = str

try:
    from pathlib import Path
except ImportError:
    Path = str


# Alternative:
#   1. Put the following statement in __init__.py
#   2. In __init__.py add: __all__ = ['PermissionError']
#   3. In this script add: 'from util import *'
if sys.version_info < (3, 0):
    import errno

    class PermissionError(OSError):
        """Not enough permissions."""

        def __init__(self, *args, **kwargs):
            """TBW."""
            super(PermissionError, self).__init__(errno.EACCES, *args, **kwargs)


class ImageData(object):
    """Parent class of all image like data.

    This class may be constructed directly with a 2d image numpy array and
    a key/value header dictionary. This class is compatible with the SensorFrame,
    and also provides a convenient class to construct images in memory with
    when constructing unittests.
    """

    def __init__(self, data, header=None):
        """TBW.

        :param data:
        :param header:
        """
        if header is None:
            header = {}
        self._data = data
        self._header = header

    def is_loaded(self):
        """Check if the image data is loaded."""
        return self._data is not None

    @property
    def data(self):
        """Return the image array."""
        return self._data

    @data.setter
    def data(self, value):
        """Set the image pixel values array."""
        self._data = value

    @property
    def header(self):
        """Return the image header dictionary."""
        return self._header

    @header.setter
    def header(self, value):
        """Set the image header dictionary."""
        self._header = value


class FitsFile(ImageData):
    """Class to read/write data from/into a FITS file.

    >>> fits_file = FitsFile(filename='hello.fits')
    >>> fits_file.data
    numpy.array([...])
    >>> fits_file.load()
    (numpy.array([...]), pyfits.header.Header(...))
    """

    def __init__(self, filename, hdu_index=0, is_readonly=False):
        """Initialize the FitsFile object.

        :param filename: filename of the FITS file
        :param hdu_index: (optional) HDU index
        :param bool is_readonly: Option to read/write or only read the FITS file

        :type filename: Path, str
        :type hdu_index: int, None
        :raises ValueError: If the hdu_index is negative
        :raises TypeError: if hdu_index is not an int
        """
        super(FitsFile, self).__init__(None, None)
        if not isinstance(hdu_index, int):
            raise TypeError('Wrong type for hdu_index. Expected: int, got: %s'
                            % repr(type(hdu_index)))

        if hdu_index < 0:
            raise ValueError('Wrong hdu_index (%i). Expected value >= 0'
                             % hdu_index)

        self._log = logging.getLogger(__name__)
        self._filename = Path(filename)
        self._hdu_index = hdu_index
        self._data = None
        self._header = None
        self._is_readonly = bool(is_readonly)

    def load(self, only_header=False):
        """Read the FITS file.

        :param bool only_header: if True then reads only the header,
                                 if False then reads the data and header.
        """
        self._log.debug("Load file: '%s', hdu_index: %i, "
                        "only_header: %s", self._filename, self._hdu_index, only_header)

        if only_header:
            self._header = pyfits.getheader(str(self._filename), ext=self._hdu_index)
        else:
            data, header = pyfits.getdata(str(self._filename), ext=self._hdu_index, header=True)

            self._data = data
            self._header = header

    def save(self, data=None, header=None, overwrite=True):
        """Save the data and header in the FITS file.

        :param data: (optional) data to write in the FITS file.
        :param header: (optional) header to write in the FITS file.
        :param bool overwrite: Option to overwrite the FITS file (if necessary).

        :type data: numpy.ndarray, None
        :type header: pyfits.header.Header, None
        :raises PermissionError:
        :raises ValueError:
        """
        if self._is_readonly:
            raise PermissionError("Cannot save the file.")

        if not self._filename.exists():
            self._log.debug("Save data in a new FITS file: '%s', hdu_index: %i",
                            self._filename, self._hdu_index)

            if data is None:
                # Load the data (and the header)
                new_data = self._data
            else:
                new_data = data

            if header is None:
                # Load (only) the header
                new_header = self._header
            else:
                new_header = header

            if new_data is None and new_header is None:
                raise ValueError("Missing 'data' and 'header'")

            assert self._hdu_index == 0

            # Get the folder parent of 'self._filename'
            folder = self._filename.parent

            if not folder.exists():
                self._log.debug("Create folder: '%s'", folder)
                folder.mkdir(parents=True)

            # Create a new FITS file
            if isinstance(header, dict):
                fits_header = pyfits.Header()
                # fits_header.update(**header)
                key_values = zip(header.keys(), header.values())
                fits_header.update(key_values)
            else:
                fits_header = header
            pyfits.writeto(str(self._filename), data, fits_header, output_verify='ignore', overwrite=overwrite)

            new_data = data
            new_header = header
        else:
            # FITS file already exists
            self._log.debug("Update data in an existing FITS file: '%s', "
                            "hdu_index: %i", self._filename, self._hdu_index)

            # TODO: check that 'self._hdu_index' < number of HDUs in the FITS file

            if data is None:
                # Load the data (and the header)
                new_data = self.data
            else:
                new_data = data

            if header is None:
                # Load (only) the header
                new_header = self.header
            else:
                new_header = header

            # Update the extension 'self._hdu_index' with data and header
            # try:
            pyfits.update(str(self._filename), new_data, new_header)
            # except PermissionError:
            #     print('File is opened or used by another process, data have been saved into file: temp.fits')
            #     pyfits.writeto(str('temp.fits'), new_data, new_header, output_verify='ignore', overwrite=overwrite)

        self._data = new_data
        self._header = new_header

    @property
    def filename(self):
        """Get the filename of the FITS file.

        :return: the filename
        :rtype: str
        """
        return self._filename

    @filename.setter
    def filename(self, new_path):
        """TBW.

        :param str new_path: may also be a Path type
        """
        if isinstance(new_path, str):
            self._filename = Path(new_path)
        else:
            self._filename = new_path

    @property
    def hdu_index(self):
        """Get the current HDU index.

        :return: the index
        :rtype: int
        """
        return self._hdu_index

    @property
    def data(self):
        """Get the data from the FITS file. Load the FITS file if necessary.

        :return:
        :rtype: numpy.ndarray
        """
        if self._data is None:
            # Load 'data' and 'header'
            self.load()

        return self._data

    @data.setter
    def data(self, value):
        """Write data in the FITS file.

        :param numpy.ndarray value:
        """
        self._log.debug("In filename '%s', set data", self._filename)
        self.save(data=value, header=self._header)

    @property
    def header(self):
        """Get the header from the FITS file.

        Load only the header from the FITS file if necessary.

        :return: the header
        :rtype: pyfits.header.Header
        """
        if self._header is None:
            # Load only 'header'
            self.load(only_header=True)

        return self._header

    @header.setter
    def header(self, value):
        """Write the header in the FITS file.

        :param value: the header to write
        :type value: pyfits.header.Header
        """
        self._log.debug("In filename '%s', set header", self._filename)
        self.save(data=self._data, header=value)

    @property
    def is_readonly(self):
        """Return the reading/writing modes of the FITS file.

        :return: if True then the file is only available in read mode.
        :rtype: bool
        """
        return self._is_readonly


class HeaderAccess(object):
    """Convenience class to convert a dictionary of Fits header into a test-bench independent manner."""

    class Attributes(object):
        """Header attribute class definition.

        This class will be constructed dynamically in the to_object
        routine and will enable header access using attribute de-referencing.
        """

    @classmethod
    def entry_generator(cls):
        """TBW.

        Used internally to iterate of the header class dictionary entries.
        """
        keys = [key for key in cls.__dict__.keys() if not key.startswith('__')]
        for entry_name in keys:
            entry = cls.__dict__[entry_name]
            if isinstance(entry, tuple):
                fits_name = entry[0]
                entry_type = entry[1]
                if len(entry) >= 3:
                    entry_default = entry[2]
                else:
                    entry_default = entry_type()
                yield fits_name, entry_name, entry_type, entry_default

    # @classmethod
    # def to_list(cls, header):
    #     """ Retrieve the list of header values in the order that they
    #     are defined in the header class. """
    #     result = []
    #     for fits_name, _, entry_type, entry_default in cls.entry_generator():
    #         if fits_name in header:
    #             value = entry_type(header[fits_name])
    #         else:
    #             value = entry_default
    #         result.append(value)
    #     return result

    @classmethod
    def to_dict(cls, header):
        """Convert Fits header to dict object.

        Retrieve the dictionary of key/value pairs where the key is the
        string representation of the header class attribute, and the value is
        the builtin type dependent on the header class type information.
        """
        result = {}
        for fits_name, entry_name, entry_type, entry_default in cls.entry_generator():
            if fits_name in header:
                try:
                    value = entry_type(header[fits_name])
                except KeyError:
                    value = entry_type()  # fits_name no in header
                except ValueError:
                    value = entry_type()  # conversion to type with default value failed.
                    # TODO: log this exception but keep going with default value
                    # raise
            else:
                value = entry_default
            result[entry_name] = value
        return result

    @classmethod
    def to_object(cls, header):
        """Convert the header to a HeaderAccess.Attributes instance.

        This enables the result to be dereference by direct attribute
        access (not key string).
        """
        dict_res = cls.to_dict(header)
        keys = list(dict_res.keys())
        result = HeaderAccess.Attributes()
        for key in keys:
            setattr(result, key, dict_res[key])
        return result


class FileCollector(object):
    """A class that gathers files in a directory and groups them into lists."""

    def __init__(self, file_template, header_class=None,
                 criteria_func=None, group_values=None, file_nums=None):
        """TBW.

        :param file_template:
        :param header_class:
        :param criteria_func:
        :param group_values:
        :param file_nums:
        """
        self._index = -1
        files = glob.glob(file_template)
        files.sort()
        logging.debug('FileCollector: found %d files, using template: %s',
                      len(files), file_template)

        if file_nums is not None:
            logging.debug('FileCollector: constructing files list from file numbers: %s',
                          repr(file_nums))
            files_per_group = self.numbered_files(file_template, file_nums, header_class, criteria_func)

        elif group_values is not None:
            logging.debug('FileCollector: constructing files list from groups: %s',
                          repr(group_values))
            files_per_group = self.group_files(header_class, files, group_values, criteria_func)
        elif criteria_func is not None:
            logging.debug('FileCollector: constructing files list from criteria: %s',
                          repr(criteria_func))
            files_per_group = [self.filter_files(header_class, files, criteria_func)]
        else:
            logging.debug('FileCollector: constructing files list from template: %s',
                          file_template)
            files_per_group = [files]

        self._files_per_group = files_per_group

    def __getitem__(self, index):
        """TBW."""
        return self._files_per_group[index]

    def __len__(self):
        """TBW."""
        return len(self._files_per_group)

    def __iter__(self):
        """TBW."""
        return self

    def next(self):  # Python 3: def __next__(self)
        """TBW."""
        self._index += 1
        if 0 <= self._index < len(self._files_per_group):
            return self._files_per_group[self._index]
        self._index = -1
        raise StopIteration

    def get_grouped_files(self):
        """TBW."""
        return self._files_per_group

    @staticmethod
    def filter_files(header, files, criteria):
        """TBW.

        :param HeaderAccess header:
        :param list files:
        :param callable criteria:
        :return: 1d list of file paths
        :rtype: list
        :raises TypeError:
        """
        if not callable(criteria):
            raise TypeError('Invalid criteria argument: %s' % repr(criteria))

        argspec = inspect.getargspec(criteria)
        if len(argspec.args) != 1:
            raise TypeError('Criteria function does not have the correct number '
                            'of argument. Expected 1, got: %d' % len(argspec.args))

        files_filtered = []
        for fits_file in files:
            fits = FitsFile(fits_file)
            row = header.to_object(fits.header)
            if criteria(row):
                files_filtered.append(fits_file)
        return files_filtered

    @staticmethod
    def group_files(header, files, groups, criteria):
        """TBW.

        :param HeaderAccess header:
        :param list files:
        :param list groups: a sequence of values to group the
            files with.
        :param callable criteria:
        :return: list of lists. The first list will correspond
            to the first group, the 2nd with the 2nd group, and so on.
        :rtype: list
        :raises TypeError:
        """
        if isinstance(header, type) and not isinstance(header(), HeaderAccess):
            raise TypeError('Invalid header argument: %s' % repr(header))

        if not isinstance(header, type) and not isinstance(header, HeaderAccess):
            raise TypeError('Invalid header argument: %s' % repr(header))

        if not callable(criteria):
            raise TypeError('Invalid criteria argument: %s' % repr(criteria))

        argspec = inspect.getargspec(criteria)
        if len(argspec.args) != 2:
            raise TypeError('Criteria function does not have the correct number '
                            'of arguments. Expected 2, got: %d' % len(argspec.args))

        files_list = [[] for _ in groups]
        for fits_file in files:
            fits = FitsFile(fits_file)
            row = header.to_object(fits.header)
            logging.debug('header: %s', repr(row.__dict__))
            for i, value in enumerate(groups):
                if criteria(row, value):
                    files_list[i].append(fits_file)
        logging.debug('group_files: %s', repr(files_list))
        return files_list

    @staticmethod
    def numbered_files(file_template, file_nums, header, criteria):
        """TBW.

        :param str file_template:
        :param list file_nums:
        :param Header header:
        :param callable criteria:
        :return: list of file lists
        :rtype: list[list[str]]]
        :raises TypeError: if file_nums argument is not a list.
        :raises IndexError: if the file_nums argument list is empty.
        :raises SyntaxError: if the file template does not contain a placeholder
            sub-string.
        """
        if '{' in file_template and '}' in file_template:
            use_format = True
        elif '%' in file_template:
            use_format = False
        else:
            raise SyntaxError('Incorrect "template" format. Expected a placeholder. '
                              'file_template: %s' % repr(file_template))

        # if isinstance(file_nums, range):
        #     file_nums = list(file_nums)
        #
        # if not isinstance(file_nums, list):
        #     raise TypeError('Incorrect type for "file_nums" argument. '
        #                     'A list was expected, got: %s.' % repr(type(file_nums)))

        if len(file_nums) == 0:
            raise IndexError('Incorrect length if "file_nums" argument.'
                             'Expected 1 or more, got 0.')

        file_nums_groups = file_nums
        if isinstance(file_nums[0], int):
            file_nums_groups = [file_nums]

        files_per_group = []
        for group in file_nums_groups:
            files = []
            for num in group:
                if use_format:
                    file_path = file_template.format(num)
                else:
                    file_path = file_template % num

                if os.path.exists(file_path):
                    if criteria:
                        fits = FitsFile(file_path)
                        row = header.to_object(fits.header)
                        if criteria(row):
                            files.append(file_path)
                    else:
                        files.append(file_path)
                else:
                    break
            files_per_group.append(files)

        return files_per_group
