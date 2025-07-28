#  Copyright (c) YOUR COPYRIGHT HERE

"""
apply_gain module for the PyXel simulation.

This module is used in data_processing

-------------------------------------------------------------------------------

+--------------+----------------------------------+---------------------------+
| Author       | Name                             | Creation                  |
+--------------+----------------------------------+---------------------------+
| You          | apply_gain                        | Wed Jul 23 10:35:47 2025                   |
+--------------+----------------------------------+---------------------------+

+-----------------+-------------------------------------+---------------------+
| Contributor     | Name                                | Creation            |
+-----------------+-------------------------------------+---------------------+
| Name            | filename                            | 06/21/2019          |
+-----------------+-------------------------------------+---------------------+

This is a documentation template for the apply_gain module.
This docstring can be used for automatic doc generation and explain more
in detail what the apply_gain module does in PyXel.

This module can be found in pyxel/models/data_processing.
Please modify the docstrings accordingly to provide the users a simple and
detailed explanation of your algorithm for this module.

Table examples
==============

===============  ==============================================================
Table entries    Table values
===============  ==============================================================
Entry 1          Value 1
Entry 2          Value 2
Entry 3          Value 3

Entry 4          Value 4

Entry 5          Value 5
===============  ==============================================================

+------------------------+------------+----------+----------+
| Header row, column 1   | Header 2   | Header 3 | Header 4 |
| (header rows optional) |            |          |          |
+========================+============+==========+==========+
| body row 1, column 1   | column 2   | column 3 | column 4 |
+------------------------+------------+----------+----------+
| body row 2             | Cells may span columns.          |
+------------------------+------------+---------------------+
| body row 3             | Cells may  | - Table cells       |
+------------------------+ span rows. | - contain           |
| body row 4             |            | - body elements.    |
+------------------------+------------+----------+----------+
| body row 5             | Cells may also be     |          |
|                        | empty: ``-->``        |          |
+------------------------+-----------------------+----------+

Code example
============

.. code-block:: python

    import sys

    print("Hello world...")


.. literalinclude:: pyxel/models/data_processing/apply_gain.py
    :language: python
    :linenos:
    :lines: 84-87

Model reference in the YAML config file
=======================================

.. code-block:: yaml

    pipeline:

      # Small comment on what it does
      data_processing:
        - name: apply_gain
          func: pyxel.models.data_processing.apply_gain.model
          enabled: true
          arguments:
            arg1: data/fits/Pleiades_HST.fits
            arg2: true
            arg3: 42

Useful links
============

ReadTheDocs documentation
https://sphinx-rtd-theme.readthedocs.io/en/latest/index.html

.. todo::

   Write the documentation for apply_gain

"""

# One or the other
from pyxel.detectors import Detector


def apply_gain(detector: Detector) -> None:
    """Apply the gain array specified in the detector's characteristics

    Parameters
    ----------
    detector: Detector

    Returns
    -------
    None
    """

    detector.data["n_array"] = detector.image.array * detector.characteristics.gain_array

    return None
