#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Simple model to load charge profiles."""

from pathlib import Path
from typing import TYPE_CHECKING, Literal

from pyxel.detectors import Detector, Geometry
from pyxel.models import Metadata, MetadataModel
from pyxel.util import load_cropped_and_aligned_image

if TYPE_CHECKING:
    import numpy as np


def load_charge(
    detector: Detector,
    filename: str | Path,
    position: tuple[int, int] = (0, 0),
    align: (
        Literal["center", "top_left", "top_right", "bottom_left", "bottom_right"] | None
    ) = None,
    time_scale: float = 1.0,
) -> None:
    """Load charge from txt file for detector, mostly for but not limited to :term:`CCDs<CCD>`.

    Parameters
    ----------
    detector : Detector
        Pyxel Detector object.
    filename : str or Path
        File path.
    position : tuple
        Indices of starting row and column, used when fitting charge to detector.
    align : Literal
        Keyword to align the charge to detector. Can be any from:
        ("center", "top_left", "top_right", "bottom_left", "bottom_right")
    time_scale : float
        Time scale of the input charge, default is 1 second. 0.001 would be ms.

    Notes
    -----
    The :ref:`Pixel coordinate conventions <pixel_coordinate_conventions>` in Pyxel define
    the coordinate of pixel ``(0, 0)`` at the center of the leftmost bottom pyxel.

    For example, when using the parameter ``align = "bottom_left"``, the image generated will
    be aligned to the lower leftmost pixel ``(0, 0)`` like this:

    .. code-block:: bash

                   ┌─────────────┐
          top    4 │ ........... │
                 3 │ ........... │     Size: 5 x 10
       Y         2 │ xxxxx...... │     x: charge injected
                 1 │ xxxxx...... │
          bottom 0 │ xxxxx...... │
                   └─────────────┘
                     0 2 4 6 8 9
                    left    right
                          X
    """
    geo: Geometry = detector.geometry
    position_y, position_x = position

    # Load charge profile as numpy array.
    charges: np.ndarray = load_cropped_and_aligned_image(
        shape=(geo.row, geo.col),
        filename=filename,
        position_x=position_x,
        position_y=position_y,
        align=align,
    )

    new_charges = charges * detector.time_step / time_scale

    # Add charges in 'detector'
    detector.charge.add_charge_array(new_charges)


load_charge.meta = Metadata(
    name="load_charge",
    model_group="Charge Collection",
    detector="all",
    status=None,
    model=MetadataModel(
        description="""With this model you can add charge to :py:class:`~pyxel.detectors.Detector`
by loading charge values from a file.
Accepted file formats are ``.npy``, ``.fits``, ``.txt``, ``.data``, ``.jpg``, ``.jpeg``, ``.bmp``,
``.png`` and ``.tiff``. Use argument ``position`` to set the offset from (0,0) pixel
and set where the input charge is placed onto detector. You can set preset positions with argument ``align``.
Values outside of detector shape will be cropped.
Read more about placement in the documentation of function :py:func:`~pyxel.util.fit_into_array`.
Use argument ``time_scale`` to set the time scale of the input charge, default is 1 second.""",
        config="""
- name: load_charge
  func: pyxel.models.charge_generation.load_charge
  enabled: true
  arguments:
    filename: data/charge.npy
    position: [0,0]
""",
    ),
)
