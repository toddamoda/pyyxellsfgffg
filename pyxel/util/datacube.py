#   --------------------------------------------------------------------------
#   Copyright 2016 SRE-F, ESA (European Space Agency)
#       Hans Smit <Hans.Smit@esa.int>
#       Frederic Lemmel <Frederic.Lemmel@esa.int>
#   --------------------------------------------------------------------------

"""Implementation of a Datacube."""

import logging
from collections import OrderedDict

import numpy as np

from .sensor import CCDFrame
from .fitsfile import FitsFile


class DataCubeItems(object):
    """Class to access the items from the MetaDatacube."""

    def __init__(self, instance, attribute):
        """TBW.

        ... Example::

            >>> dc = MetaDatacube(param=[param0, param1, param2], dtype=Foo)
            >>> dc_items = DataCubeItems(instance=dc, attribute='val')

        :param MetaDatacube instance:
        :param str attribute:
        :raises ValueError: if the instance does not have the 'attribute'
        """
        # Check if the 'attribute' exists
        if not hasattr(instance.dtype, attribute):
            raise ValueError("Attribute '%s' is missing in "
                             "factory class '%r'" % (attribute, instance.dtype))

        self._instance = instance
        self._attribute = attribute

    def __len__(self):
        """Number of elements in the Datacube.

        ..Example::

            >>> dc = MetaDatacube(param=[param0, param1, param2], dtype=Foo)
            >>> dc_items = DataCubeItems(dc, 'val')

            >>> len(dc_items)
            3

        :return: total number of elements
        :rtype: int
        """
        return self._instance.size

    def __iter__(self):
        """Returns an iterator.

        :return: the iterator for the specified attribute
        :rtype: collections.Iterator

        ..Example::
            >>> dc = MetaDatacube(param=[param0, param1, param2], dtype=Foo)
            >>> dc_items = DataCubeItems(dc, 'val')

            >>> iter(dc_items)
            iter([Foo(param0).val, Foo(param1).val, Foo(param2).val])
        """
        # Get all the elements
        return self.__getitem__(slice(None))

    def _get_sliced_idx(self, item):
        """TBW.

        :param item:
        :type item: int, slice
        :return:
        :rtype: int, collections.Iterator

        ..Example::
            >>> dc = MetaDatacube(param=[param0, param1, param2], dtype=Foo)
            >>> dc_items = DataCubeItems(dc, 'val')

            >>> dc_items._get_sliced_idx(0)
            0

            >>> dc_items.get_idx(slice(0, 2))
            iter([0, 1])
        """
        # Get the list of all indexes (e.g. [0, 1, 2, ...] or [(0, 0), (0, 1), ...]
        indexes_flat = list(self._instance.ndindex())

        # Convert the list into a (multi-dimensional) numpy array
        indexes_np = np.array(indexes_flat).reshape(self._instance.shape)

        indexes = indexes_np[item]

        return iter(indexes.tolist())

    def __getitem__(self, item):
        """Get one value or multiple values (as an iterator).

        :param item:
        :type item: int, slice
        :return:
        :rtype: object
        :raises TypeError: if the item does not have the right type

        ..Example::
            >>> dc = MetaDatacube(param=[param0, param1, param2], dtype=Foo)
            >>> dc_items = DataCubeItems(dc, 'val')

            >>> dc_items[0]
            Foo(param0).val

            >>> dc_items[0:2]
            iter([Foo(param0).val, Foo(param1).val])
        """
        if isinstance(item, int):
            # Get only one element
            obj = self._instance.load_one_element(index=item)
            ret = getattr(obj, self._attribute)

        elif isinstance(item, slice):
            # Get all the
            indexes = self._get_sliced_idx(item)
            ret = (self.__getitem__(idx) for idx in indexes)

        else:
            raise TypeError("Wrong type for '%r'. Expected a 'int' or 'slice'" % item)

        return ret

    def __setitem__(self, key, value):
        """Set one value or multiple values (from an iterator).

        :param key:
        :param value:
        :type key: int, slice
        :type value: object, list, numpy.ndarray, collections.Iterator

        :raises TypeError: if the key doest not have the right type

        ..Example::
            >>> dc = MetaDatacube(param=[param0, param1, param2], dtype=Foo)
            >>> dc_items = DataCubeItems(dc, 'val')

            The two following assignments are equivalent:
            >>> dc_items[0] = data0
            >>> Foo[param0].val = data0

            This assignment:
            >>> dc_items[0:2] = [data0, data1]
            is equivalent to:
            >>> Foo[param0].val = data0
            >>> Foo[param1].val = data1
        """
        if isinstance(key, int):
            obj = self._instance.load_one_element(index=key)
            setattr(obj, self._attribute, value)
        elif isinstance(key, slice):

            # Get an iterator of the slices indexes (or coordinates)
            indexes = self._get_sliced_idx(key)

            for idx, val in zip(indexes, value):
                obj = self._instance.load_one_element(idx)
                setattr(obj, self._attribute, val)

        else:
            raise TypeError("Wrong type for '%r'. Expected a 'int' or 'slice'" % key)


class MetaDataCube(object):
    """Generic implementation of a Datacube.

     A Datacube is a one-(or higher) dimensional array of elements.

     The Datacube is initialized with an array of parameters ('params') and a data type ('dtype')
     The data type is used to instanciate the element(s)
     """

    def __init__(self, params, dtype, params_dtype=None, cache_capacity=1, readonly=False):
        """Create a new DataCube.

        :param params: list of parameters used to initialize the items
        :param dtype: data type of the items
        :param params_dtype: data type of the parameters
        :param cache_capacity: number of elements for the cache
        :param readonly:

        :type params: list, numpy.ndarray
        :type dtype: type
        :type params_dtype: None, numpy.dtype
        :type cache_capacity: int, None
        :type readonly: bool

        :raises TypeError: if the 'params' or 'cache_capacity' does not have the right format
        :raises ValueError: if the 'cache_capacity' is negative

        ..Example::

            >>> dc = MetaDataCube(params=['filename0', 'filename1', 'filename2'], dtype=Foo,
            ...                   params_dtype=Path, readonly=True)


            >>> dt = numpy.dtype([('filename', Path),
            ...                   ('hdu_idx', int)])
            >>> dc = MetaDataCube(params=[('filename0', 0), ('filename1', 1)], dtype=Foo,
            ...                   params_dtype=dt)

        """
        self._log = logging.getLogger(__name__)

        if not isinstance(params, (list, np.ndarray)):
            raise TypeError("Wrong type for 'params': %r. "
                            "Expected a list or numpy.ndarray" % params)

        if isinstance(cache_capacity, int):
            if cache_capacity < 0:
                raise ValueError("'cache_capacity' (%i) must be positive" % cache_capacity)
        elif cache_capacity is not None:
            raise TypeError("Wrong type for 'cache_capacity': %r. "
                            "Expected an 'int' or 'None" % cache_capacity)

        # Convert the list of 'data' into a numpy array of Path objects
        self._params_array = np.array(params, dtype=params_dtype)

        # Initialize the cache
        self._cache = OrderedDict()
        self._cache_capacity = cache_capacity
        self._cache_misses = 0
        self._cache_hits = 0
        self._dtype = dtype
        self._readonly = bool(readonly)

    @property
    def cache_capacity(self):
        """Get the number of elements that can be stored in the cache.

        :return: the cache capacity
        :rtype: int, None
        """
        return self._cache_capacity

    @property
    def cache_misses(self):
        """Get the number of cache misses.

        :return: cache misses
        :rtype: int
        """
        return self._cache_misses

    @property
    def cache_hits(self):
        """Get the number of cache hits.

        :return: cache hits
        :rtype: int
        """
        return self._cache_hits

    @property
    def shape(self):
        """Get the shape of the Datacube.

        :return: tuple of dimensions
        :rtype: tuple
        """
        return self._params_array.shape

    @property
    def ndim(self):
        """Get the number of dimension(s) of the Datacube.

        :return: number of dimensions
        :rtype: int
        """
        return self._params_array.ndim

    @property
    def size(self):
        """Get the number of elements in the Datacube.

        :return: number of elements
        :rtype: int
        """
        return self._params_array.size

    @property
    def dtype(self):
        """Data type of the items.

        :return:
        :rtype: type
        """
        return self._dtype

    @property
    def readonly(self):
        """TBW.

        :return:
        :rtype: bool
        """
        return self._readonly

    @property
    def params(self):
        """Returns a list of all parameters.

        :return: Copy of the parameters
        :rtype: list

        >>> dc = MetaDataCube(['param0', 'param1', 'param2', 'param3'], dtype=Foo)
        >>> dc.params
        ['param0', 'param1', 'param2', 'param3']
        """
        return self._params_array.tolist()

    def ndindex(self):
        """Returns a N-dimensional iterator object to index arrays.

        :return: the iterator
        :rtype: collections.Iterator

        .. Example::

            >>> dc = MetaDataCube(['param0', 'param1', 'param2', 'param3'], dtype=Foo)
            >>> dc.ndindex()
            iter([0, 1, 2, 3])

            >>> dc = MetaDataCube([['param0', 'param1', 'param2'],
            ...                    ['param3', 'param4', 'param5']], dtype=Foo)
            >>> for idx in dc.ndindex():
            ...     print(idx)
            (0, 0)
            (0, 1)
            (0, 2)
            (1, 0)
            (1, 1)
            (1, 2)
        """
        shape = self.shape

        if len(shape) == 1:
            # e.g. shape == (5, )
            return iter(range(shape[0]))
        else:
            # e.g. shape == (3, 4)
            return np.ndindex(shape)

    def __len__(self):
        """Pythonic convenience method so that the user can use `len(dc)`.

        :return: the number of elements in the data cube
        :rtype: int
        """
        return self.size

    def __iter__(self):
        """TBW.

        :return: Iterator of the objects
        :rtype: collections.Iterator

        >>> dc = MetaDataCube(['param0', 'param1'], dtype=Foo)
        >>> iter(dc)
        iter([Foo('param0'), Foo('param1')])
        """
        # Gets the iterator for the index of this Datacube
        indexes_iter = self.ndindex()

        # Create an iterator that access all the items of the Datacube
        obj_iter = (self.__getitem__(index) for index in indexes_iter)
        return obj_iter

    def __getitem__(self, item):
        """Get one or more elements from the Datacube.

        :param int item: may also be a slice type, i.e. slice(start, end, step)
        :return: New datacube if a slice is passed, else a datacube element if an int.
        :rtype: MetaDataCube
        :raises TypeError: the item has an inappropriate type

        >>> dc = MetaDataCube(['param0', 'param1', 'param2', 'param3'], dtype=Foo)
        >>> dc[1]
        Foo('param1')

        >>> dc[1:3]
        MetaDataCube(['param1', 'param2', 'param3'], dtype=Foo)
        """
        if isinstance(item, int):
            result = self.load_one_element(index=item)
        elif isinstance(item, slice):
            new_params = self._params_array[item]
            result = MetaDataCube(new_params,
                                  dtype=self._dtype,
                                  cache_capacity=self._cache_capacity)
        else:
            raise TypeError("Expected type 'int' or 'slice'")

        return result

    def _get_obj(self, params):
        """Create a new object of type 'dtype'.

        .. Example::

            >>> dc = MetaDataCube(params=..., dtype=Foo)

            >>> dc._get_obj(params=param0)
            Foo(param0)

            >>> dc._get_obj(params=[param0, param1])
            Foo(param0, param1)

            >>> dc._get_obj(params={'a': param0, 'b': param1})
            Foo(a=param0, b=param1)

        :param params: the parameters to initialized the new object
        :type params: list, dict
        :return:
        :rtype: object
        """
        if isinstance(params, (np.ndarray, np.void)):
            params = params.tolist()

        if isinstance(params, (tuple, list)):
            obj = self._dtype(*params)
        elif isinstance(params, dict):
            obj = self._dtype(**params)
        else:
            obj = self._dtype(params)

        return obj

    def load_one_element(self, index):
        """Get one element object from the MetaDataCube.

        The element could be instantiated or retrieved from the internal cache.

        :param index: index to find the element in the Datacube
        :type index: int, tuple

        :return: the object, i.e. FitsFile
        :rtype: object
        :raises IndexError:

        ..Example::
            >>> dc = MetaDataCube([param0, param1, param2], dtype=Foo)

            >>> dc.load_one_element(0)
            Foo(param0)
        """
        if not isinstance(index, int):
            raise IndexError("Wrong 'index': {!r}".format(index))

        # Maybe it would be possible to use @lru_cache(max_size=self._cache_capacity)
        if self._cache_capacity == 0:
            # No cache. Instantiate directly a new element
            params = self._params_array[index]
            obj = self._get_obj(params)

        elif self._cache_capacity == 1 or self._cache_capacity is None:
            # This is a cache with one or an unlimited capacity

            # Check if the element is already in the cache
            if index in self._cache:
                self._log.debug("Get object from cache, index: %i", index)
                obj = self._cache[index]
                self._cache_hits += 1
            else:
                if self._cache_capacity == 1:
                    # Cache with only one element. Clear the cache
                    self._cache.clear()
                else:
                    # Unlimited cache. Do nothing
                    pass

                self._cache_misses += 1
                params = self._params_array[index]
                obj = self._get_obj(params)
                self._cache[index] = obj

        else:
            # Cache with more than one element capacity

            # Check if the element is already in the cache
            if index in self._cache:
                # Get the object from the cache
                self._log.debug("Get object from cache, index: %i", index)
                obj = self._cache.pop(index)
                self._cache_hits += 1
            else:
                self._cache_misses += 1

                self._log.debug("Object not in cache. "
                                "Misses: %i, index: %i", self._cache_misses, index)

                params = self._params_array[index]
                obj = self._get_obj(params)

                if len(self._cache) >= self._cache_capacity:
                    # Cache is full. Removes the first object in the cache
                    self._cache.popitem(last=False)

            # Add the object at the last position in the cache
            self._cache[index] = obj

        return obj


class FitsDataCube(MetaDataCube):
    """FitsFile data cube."""

    def __init__(self, data, cache_capacity=1):
        """Create a Datacube of FITS files.

        :param data: list of strings or Path
        :param int cache_capacity:
        :type data: list, np.ndarray
        """
        super(FitsDataCube, self).__init__(params=data,
                                           dtype=FitsFile,
                                           cache_capacity=cache_capacity)

        self._data = DataCubeItems(instance=self, attribute='data')
        self._header = DataCubeItems(instance=self, attribute='header')

    @property
    def data(self):
        """Return the 2d image pixel array."""
        return self._data

    @property
    def header(self):
        """Return the dictionary like key/value header."""
        return self._header


class CCDDataCube(MetaDataCube):
    """Datacube for the CCDs."""

    def __init__(self, data, cache_capacity=1):
        """Create a CCD datacube.

        :param data: list of str or Path
        :param int cache_capacity:
        :type data: list, np.ndarray
        """
        super(CCDDataCube, self).__init__(params=data,
                                          dtype=CCDFrame,
                                          cache_capacity=cache_capacity)

        self._box = DataCubeItems(instance=self, attribute='box')

    @property
    def box(self):
        """Retrieve the box."""
        return self._box
