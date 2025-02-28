#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.


"""Simple Inter Pixel Capacitance model: https://iopscience.iop.org/article/10.1088/1538-3873/128/967/095001/pdf."""

import numpy as np
from astropy.convolution import convolve_fft

from pyxel.detectors import CMOS
from pyxel.models import Metadata, MetadataModel


def ipc_kernel(
    coupling: float, diagonal_coupling: float = 0.0, anisotropic_coupling: float = 0.0
) -> np.ndarray:
    """Return the IPC convolution kernel from the input coupling parameters.

    Parameters
    ----------
    coupling : float
    diagonal_coupling : float
    anisotropic_coupling : float

    Returns
    -------
    np.ndarray
        Kernel.
    """

    if not diagonal_coupling < coupling:
        raise ValueError("Requirement diagonal_coupling <= coupling is not met.")
    if not anisotropic_coupling < coupling:
        raise ValueError("Requirement anisotropic_coupling <= coupling is not met.")
    if not 0 <= coupling + diagonal_coupling <= 0.25:
        raise ValueError("Requirement coupling + diagonal_coupling << 1 is not met.")

    kernel = np.array(
        [
            [diagonal_coupling, coupling - anisotropic_coupling, diagonal_coupling],
            [
                coupling + anisotropic_coupling,
                1 - 4 * (coupling + diagonal_coupling),
                coupling + anisotropic_coupling,
            ],
            [diagonal_coupling, coupling - anisotropic_coupling, diagonal_coupling],
        ],
        dtype=float,
    )

    return kernel


def compute_ipc_convolution(
    input: np.ndarray,  # noqa: A002
    coupling: float,
    diagonal_coupling: float,
    anisotropic_coupling: float,
) -> np.ndarray:
    """Compute convolution of the array with IPC kernel.

    Parameters
    ----------
    input : ndarray
    coupling : float
    diagonal_coupling : float
    anisotropic_coupling : float

    Returns
    -------
    ndarray
    """
    kernel = ipc_kernel(
        coupling=coupling,
        diagonal_coupling=diagonal_coupling,
        anisotropic_coupling=anisotropic_coupling,
    )

    # Convolution, extension on the edges with the mean value
    mean = np.mean(input)
    array = convolve_fft(input, kernel, boundary="fill", fill_value=mean)

    return array


def simple_ipc(
    detector: "CMOS",
    coupling: float,
    diagonal_coupling: float = 0.0,
    anisotropic_coupling: float = 0.0,
) -> None:
    """Convolve pixel array with the IPC kernel.

    Parameters
    ----------
    detector : CMOS
    coupling : float
    diagonal_coupling : float
    anisotropic_coupling : float

    Notes
    -----
    For more information, you can find examples here:

    * :external+pyxel_data:doc:`examples/models/inter_pixel_capacitance/ipc`
    * :external+pyxel_data:doc:`use_cases/HxRG/h2rg`
    """
    if not isinstance(detector, CMOS):
        raise TypeError("Expecting a CMOS object for detector.")

    array = compute_ipc_convolution(
        input=detector.pixel.array,
        coupling=coupling,
        diagonal_coupling=diagonal_coupling,
        anisotropic_coupling=anisotropic_coupling,
    )

    detector.pixel.array = array


simple_ipc.meta = Metadata(
    name="simple_ipc",
    model_group="Charge Collection",
    detector="all",
    status=None,
    model=MetadataModel(
        description=r"""This model can be used to apply inter-pixel capacitance to :py:class:`~pyxel.data_structure.Pixel` array.
When there is IPC, the signal read out on any pixel is affected by the signal in neighboring pixels.
The IPC affects the point spread function (PSF) of the optical system, modiying the shape of the objects.
More about the IPC and the math describing it can be found in :cite:p:`Kannawadi_2016`.
The amount of coupling between the pixels is described in the article by a
:math:`3\times3` matrix :math:`K_{\alpha, \alpha_+, \alpha'}`:

.. math::
    K_{\alpha, \alpha_+, \alpha'} = \begin{bmatrix}
    \alpha' & \alpha-\alpha_+ & \alpha'\\
    \alpha+\alpha_+ & 1-4(\alpha+\alpha') & \alpha+\alpha_+\\
    \alpha' & \alpha-\alpha_+ & \alpha'
    \end{bmatrix},

where :math:`\alpha` is the coupling parameter for the neighbouring pixels,
:math:`\alpha'` the coupling parameter for the pixels located on the diagonals
and :math:`\alpha_+` parameter for introducing an anisotropical coupling. In the model, the last two are optional.
The sum of the matrix elements is always 1.
The result image that is seen on the detector is a convolution of the image with the kernel matrix,
which is done using ``astropy`` convolution tools.""",
        config="""
- name: simple_ipc
  func: pyxel.models.charge_collection.simple_ipc
  enabled: true
  arguments:
      coupling: 0.1
      diagonal_coupling: 0.05
      anisotropic_coupling: 0.03
""",
        notebooks=[
            "examples/models/inter_pixel_capacitance/ipc",
            "use_cases/HxRG/h2rg",
        ],
    ),
)
