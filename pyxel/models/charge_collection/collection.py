#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Pyxel charge collection model."""

from pyxel.detectors import Detector
from pyxel.models import Metadata, MetadataModel


def simple_collection(detector: Detector) -> None:
    """Associate charge with the closest pixel.

    Parameters
    ----------
    detector : Detector
        Pyxel Detector object.
    """
    detector.pixel.array += detector.charge.array


simple_collection.meta = Metadata(
    name="simple_collection",
    model_group="Charge Collection",
    detector="all",
    status=None,
    model=MetadataModel(
        description="""Simple collection model is the simplest model of charge collection and
necessary to fill up :py:class:`~pyxel.data_structure.Pixel` array when no other collection model is used.
If charge inside :py:class:`~pyxel.data_structure.Charge` class is stored in an ``numpy`` array,
arrays will be the same. If charge is in the form of ``Pandas`` dataframe and
representing 3D point cloud of charges inside the detector,
calling ``array`` property of :py:class:`~pyxel.data_structure.Charge`
will assign charges to the closest pixel and sum the values.
    """,
        config="""
- name: simple_collection
  func: pyxel.models.charge_collection.simple_collection
  enabled: true
  """,
    ),
)
