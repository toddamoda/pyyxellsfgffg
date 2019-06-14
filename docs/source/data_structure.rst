.. _data_structure:

Data Structure
================

Models in Pyxel should be able to add photons, charges,
charge packets, signal or image pixel values to the corresponding
data structure classes (Photon, Charge, Pixel, Signal or Image class).

These classes are storing the data values
either inside a Pandas DataFrame or in a NumPy array. Via DataFrame or
NumPy array handling functions, models can also modify properties of photons,
charges, etc., like position, kinetic energy,
number of electrons per charge packet, signal amplitude, etc.

DataFrame and Array classes and their methods to store and handle the
data in Pyxel:


.. currentmodule:: pyxel.data_structure.array
.. autoclass:: Array
    :special-members:
    :exclude-members: __eq__, __ge__, __gt__, __le__, __lt__, __ne__, __repr__, __weakref__
    :members:


.. currentmodule:: pyxel.data_structure.charge
.. autoclass:: Charge
    :special-members:
    :exclude-members: __eq__, __ge__, __gt__, __le__, __lt__, __ne__, __repr__, __weakref__
    :members:


.. currentmodule:: pyxel.data_structure.image
.. autoclass:: Image
    :special-members:
    :exclude-members: __eq__, __ge__, __gt__, __le__, __lt__, __ne__, __repr__, __weakref__
    :members:


.. currentmodule:: pyxel.data_structure.particle
.. autoclass:: Particle
    :special-members:
    :exclude-members: __eq__, __ge__, __gt__, __le__, __lt__, __ne__, __repr__, __weakref__
    :members:


.. currentmodule:: pyxel.data_structure.photon
.. autoclass:: Photon
    :special-members:
    :exclude-members: __eq__, __ge__, __gt__, __le__, __lt__, __ne__, __repr__, __weakref__
    :members:


.. currentmodule:: pyxel.data_structure.pixel
.. autoclass:: Pixel
    :special-members:
    :exclude-members: __eq__, __ge__, __gt__, __le__, __lt__, __ne__, __repr__, __weakref__
    :members:


.. currentmodule:: pyxel.data_structure.signal
.. autoclass:: Signal
    :special-members:
    :exclude-members: __eq__, __ge__, __gt__, __le__, __lt__, __ne__, __repr__, __weakref__
    :members:
