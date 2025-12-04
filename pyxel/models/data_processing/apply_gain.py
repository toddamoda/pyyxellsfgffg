#  Copyright (c) University College London, 2025.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""
apply_gain module for the PyXel simulation.

This module is used in data_processing

-------------------------------------------------------------------------------

+--------------+----------------------------------+---------------------------+
| Author       | Name                             | Creation                  |
+--------------+----------------------------------+---------------------------+
| Zach Clare   | apply_gain                       | Wed Jul 23 10:35:47 2025  |
+--------------+----------------------------------+---------------------------+

+-----------------+-------------------------------------+---------------------+
| Contributor     | Name                                | Creation            |
+-----------------+-------------------------------------+---------------------+
| Zach Clare      | apply_gain.py                       | 07/23/2025          |
+-----------------+-------------------------------------+---------------------+

This module applies the gain array to the image array. Multiplication is done
element-wise and saved to the data array with the key "n_array". It can be
accessed with `detector.data['n_array']`.

Model reference in the YAML config file
=======================================

.. code-block:: yaml

    pipeline:

      # Small comment on what it does
      data_processing:
        - name: apply_gain
          func: pyxel.models.data_processing.apply_gain
          enabled: true

"""

# One or the other
from pyxel.detectors import Detector


def apply_gain(detector: Detector) -> None:
	"""Apply the gain array specified in the detector's characteristics. The array
	is loaded in ``Characteristics.Initialze()``, which is called automatically
	when the `.yaml` congifuration file is loaded.
	Parameters
	----------
	detector: Detector
	Returns
	-------
	None
	"""

	try:
		detector.data["n_array"] = detector.image.array * detector.characteristics.gain_array
	except AttributeError as e:
		raise AttributeError("Ensure 'gain_array_path' is specified in the Detector's characteristics.") from e
	
	return None
