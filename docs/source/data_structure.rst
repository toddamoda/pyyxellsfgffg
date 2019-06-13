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
