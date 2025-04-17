#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Linearity models."""

from collections.abc import Sequence

import numpy as np
import xarray as xr
from astropy import constants as const

from pyxel.detectors import CMOS, Detector
from pyxel.models import Metadata, MetadataModel, YAMLConfig
from pyxel.models.charge_measurement.non_linearity_calculation import (
    euler,
    hgcdte_bandgap,
    ni_hansen,
)


def compute_poly_linearity(
    array_2d: np.ndarray,
    coefficients: Sequence[float],
) -> np.ndarray:
    """Add non-linearity to an array of values following a polynomial function.

    Parameters
    ----------
    array_2d : ndarray
        Input array.
    coefficients : list of float
        Coefficients of the polynomial function.

    Returns
    -------
    np.ndarray
        Signal.
    """
    polynomial_function = np.polynomial.polynomial.Polynomial(coefficients)

    non_linear_signal = polynomial_function(array_2d)

    return non_linear_signal


def output_node_linearity_poly(
    detector: Detector,
    coefficients: Sequence[float],
) -> None:
    """Add non-linearity to signal array to simulate the non-linearity of the output node circuit.

    The non-linearity is simulated by a polynomial function. The user specifies the polynomial coefficients.

    detector Signal unit: Volt

    Parameters
    ----------
    detector : Detector
        Pyxel Detector object.
    coefficients : list of float
        Coefficient of the polynomial function.

    Notes
    -----
    For more information, you can find examples here:

    * :external+pyxel_data:doc:`use_cases/CCD/euclid_prnu`
    * :external+pyxel_data:doc:`use_cases/HxRG/h2rg`
    * :external+pyxel_data:doc:`workshops/leiden_university_workshop/ptc`
    """
    if len(coefficients) == 0:
        raise ValueError("Length of coefficient list should be more than 0.")

    signal_mean_array = detector.signal.array.astype("float64")
    signal_non_linear = compute_poly_linearity(
        array_2d=signal_mean_array, coefficients=coefficients
    )

    signal_non_linear = signal_non_linear.clip(min=0.0)
    detector.signal.array = signal_non_linear


output_node_linearity_poly.meta = Metadata(
    name="output_node_linearity_poly",
    model_group="Charge Measurement",
    detector="all",
    status=None,
    model=MetadataModel(
        description="""With this model you can add non-linearity to :py:class:`~pyxel.data_structure.Signal` array
to simulate the non-linearity of the output node circuit.
The non-linearity is simulated by a polynomial function.
The user specifies the polynomial coefficients with the argument ``coefficients``:
a list of :math:`n` floats e.g. :math:`[a,b,c] \rightarrow S = a + bx+ cx2` (:math:`x` is signal).
""",
        config=YAMLConfig(
            description="Example of the configuration file where a 10% non-linearity is introduced as "
            "a function of the signal square:",
            config="""
- name: linearity
  func: pyxel.models.charge_measurement.output_node_linearity_poly
  enabled: true
  arguments:
    coefficients: [0, 1, 0.9]  # e- [a,b,c] -> S = a + bx+ cx2 (x is signal)
""",
        ),
        notebooks=[
            ":external+pyxel_data:doc:`use_cases/CCD/euclid_prnu`",
            ":external+pyxel_data:doc:`use_cases/HxRG/h2rg`",
            ":external+pyxel_data:doc:`workshops/leiden_university_workshop/ptc`",
        ],
    ),
)


def compute_simple_physical_non_linearity(
    array_2d: np.ndarray,
    temperature: float,  # Detector operating temperature
    v_bias: float,
    cutoff: float,
    n_acceptor: float,
    n_donor: float,
    diode_diameter: float,
) -> np.ndarray:
    """Compute simple physical non-linear signal.

    Parameters
    ----------
    array_2d : ndarray
        Input array.
    temperature
        Temperature. Unit: K.
    v_bias : float
        Initial bias voltage. Unit: V.
    cutoff : float
        Cutoff wavelength. unit: um
    n_acceptor : float
        Acceptor density. Unit: atoms/cm^3
    n_donor : float
        Donor density. Unit: atoms/cm^3
    diode_diameter : float
        Diode diameter. Unit: um

    Returns
    -------
    ndarray
        Output array.
    """
    # Derivation of Cd concentration in the alloy,  it depends on cutoff wavelength and targeted operating temperature
    # Here we are considering the case where the detector is operated at its nominal temperature,
    # it might not be always the case
    # cutoff = 2.1
    e_g_targeted = 1.24 / cutoff  # cutoff is um and Eg in eV
    xcd = np.linspace(0.2, 0.6, 1000)
    targeted_operating_temperature = temperature
    e_g_calculated = hgcdte_bandgap(
        x_cd=xcd,
        temperature=targeted_operating_temperature,
    )  # Expected bandgap

    index = np.where(e_g_calculated > e_g_targeted)[0][0]
    x_cd = xcd[index]  # Targeted cadmium concentration in the HgCdTe alloy

    # Calculate the effective band-gap value at the temperature at which simulations are performed.
    ni = ni_hansen(x_cd=x_cd, temperature=temperature)

    if np.isclose(ni, 0.0):
        raise ValueError(
            "Intrinsic carrier concentration is equal to zero "
            f"with {x_cd=} and {temperature=}"
        )

    # Build in potential
    vbi = (
        const.k_B.value
        * temperature
        / const.e.value
        * np.log(n_acceptor * n_donor / ni**2)
    )

    # HgCdTe dielectric constant
    eps = 20.5 - 15.6 * x_cd + 5.7 * x_cd**2

    # Surface of the diode, assumed to be planar
    surface = (
        np.pi * (diode_diameter / 2.0 * 1e-6) ** 2
    )  # Surface of the diode, assumed to be circular

    # Initial value  of the diode capacitance
    co = surface * np.sqrt(
        (const.e.value * eps * const.eps0.value)
        / (2 * (vbi - v_bias))
        * ((n_acceptor * 1e6 * n_donor * 1e6) / (n_acceptor * 1e6 + n_donor * 1e6))
    )

    non_linear_signal = (
        1
        / (2 * vbi)
        * (const.e.value * array_2d / co) ** 2
        * (-1 + np.sqrt(1 + 4 * (co / (const.e.value * array_2d)) ** 2 * vbi**2))
    )

    return non_linear_signal


def simple_physical_non_linearity(
    detector: CMOS,
    cutoff: float,
    n_acceptor: float,
    n_donor: float,
    diode_diameter: float,
    v_bias: float,
) -> None:
    """Apply simple physical non-linearity.

    Parameters
    ----------
    detector : Detector
        Pyxel detector object.
    cutoff : float
        Cutoff wavelength. unit: um
    n_donor : float
        Donor density. Unit: atoms/cm^3
    n_acceptor : float
        Acceptor density. Unit: atoms/cm^3
    diode_diameter : float
        Diode diameter. Unit: um
    v_bias : float
        Initial bias voltage. Unit: V.
    """

    if not (4 <= detector.environment.temperature <= 300):
        raise ValueError(
            "Hansen bangap expression used out of its nominal application range. "
            "temperature must be between 4K and 300K"
        )

    if not isinstance(detector, CMOS):
        raise TypeError("Expecting a 'CMOS' detector object.")

    signal_mean_array = detector.charge.array.astype("float64")
    signal_non_linear = compute_simple_physical_non_linearity(
        array_2d=signal_mean_array,
        temperature=detector.environment.temperature,
        v_bias=v_bias,
        cutoff=cutoff,
        n_acceptor=n_acceptor,
        n_donor=n_donor,
        diode_diameter=diode_diameter,
    )

    detector.signal.array = signal_non_linear


simple_physical_non_linearity.meta = Metadata(
    name="simple_physical_non_linearity",
    model_group="Charge Measurement",
    detector="CMOS",
    status=None,
    model=MetadataModel(
        description="""With this model you can add non-linearity to :py:class:`~pyxel.data_structure.Signal` array.

The model assumes a planar geometry of the diode and
follows the description of the classical non-linearity model described in :cite:p:`Plazas_2017`.
It does not take into account the additional fixed capacitance and the gain non-linearity
and does not simulate saturation.""",
        notes="This model is specific to the :term:`CMOS` detector.",
        config="""
- name: simple_physical_non_linearity
  func: pyxel.models.charge_measurement.simple_physical_non_linearity
  enabled: true
  arguments:
    cutoff: 2.1
    n_acceptor: 1.e+18
    n_donor: 3.e+15
    diode_diameter: 10.
    v_bias: 0.1
""",
    ),
)


def compute_physical_non_linearity(
    array_2d: np.ndarray,
    temperature: float,
    fixed_capacitance: float,
    v_bias: float,
    cutoff: float,
    n_acceptor: float,
    n_donor: float,
    diode_diameter: float,
) -> np.ndarray:
    """Compute physical non-linear signal.

    Parameters
    ----------
    array_2d : ndarray
        Input array.
    temperature
        Temperature. Unit: K.
    fixed_capacitance : float
        Additional fixed capacitance. Unit: F
    v_bias : float
        Initial bias voltage. Unit: V.
    cutoff : float
        Cutoff wavelength. unit: um
    n_acceptor : float
        Acceptor density. Unit: atoms/cm^3
    n_donor : float
        Donor density. Unit: atoms/cm^3
    diode_diameter : float
        Diode diameter. Unit: um

    Returns
    -------
    ndarray
        Output array.
    """
    # Derivation of Cd concentration in the alloy,  it depends on cutoff wavelength and targeted operating temperature
    # Here we are considering the case where the detector is operated at its nominal temperature,
    # it might not be always the case
    e_g_targeted = 1.24 / cutoff  # cutoff is um and Eg in eV
    xcd = np.linspace(start=0.2, stop=0.6, num=1000)
    targeted_operating_temperature = temperature

    # Expected band-gap
    e_g_calculated = hgcdte_bandgap(
        x_cd=xcd, temperature=targeted_operating_temperature
    )

    index = np.where(e_g_calculated > e_g_targeted)[0][0]
    x_cd = xcd[index]  # Targeted cadmium concentration in the HgCdTe alloy

    # Calculate the effective band-gap value at the temperature at which simulations are performed.
    ni = ni_hansen(x_cd=x_cd, temperature=temperature)

    if np.isclose(ni, 0.0):
        raise ValueError(
            "Intrinsic carrier concentration is equal to zero "
            f"with {x_cd=} and {temperature=}"
        )

    # Build in potential
    vbi = (
        const.k_B.value
        * temperature
        / const.e.value
        * np.log(n_acceptor * n_donor / ni**2)
    )  # in V

    # HgCdTe dielectric constant
    eps = 20.5 - 15.6 * x_cd + 5.7 * x_cd**2  # without dimension

    # Surface of the diode, assumed to be planar
    surface = (
        np.pi * (diode_diameter / 2.0 * 1e-6) ** 2
    )  # Surface of the diode, assumed to be circular (in cm)

    # Initial value  of the diode capacitance
    co = surface * np.sqrt(
        (const.e.value * eps * const.eps0.value)
        / (2 * vbi)
        * ((n_acceptor * 1e6 * n_donor * 1e6) / (n_acceptor * 1e6 + n_donor * 1e6))
    )

    # Resolution of 2nd order equation
    b = -2.0 * co / fixed_capacitance
    a = -1.0
    c = (
        (1 - v_bias / vbi)
        + 2.0 * co / fixed_capacitance * np.sqrt(1.0 - v_bias / vbi)
        - array_2d * const.e.value / (fixed_capacitance * vbi)
    )
    discriminant = b**2 - 4.0 * c * a
    u1 = (-b - np.sqrt(discriminant)) / (2.0 * a)
    v1 = (1.0 - u1**2) * vbi - v_bias  # is subtracted it only deals with offset level

    array = np.copy(v1)  # unit if V, voltage at the gate of the pixel SFD
    non_linear_signal = array.astype("float64")

    return non_linear_signal


def physical_non_linearity(
    detector: CMOS,
    cutoff: float,
    n_acceptor: float,
    n_donor: float,
    diode_diameter: float,
    v_bias: float,
    fixed_capacitance: float,
) -> None:
    """Apply physical non-linearity.

    Parameters
    ----------
    detector : Detector
        Pyxel detector object.
    cutoff : float
        Cutoff wavelength. unit: um
    n_donor : float
        Donor density. Unit: atoms/cm^3
    n_acceptor : float
        Acceptor density. Unit: atoms/cm^3
    diode_diameter : float
        Diode diameter. Unit: um
    v_bias : float
        Initial bias voltage. Unit: V.
    fixed_capacitance : float
        Additional fixed capacitance. Unit: F

    Notes
    -----
    For more information, you can find an example here:
    :external+pyxel_data:doc:`examples/models/non_linearity/non_linearity`.
    """
    if not (4 <= detector.environment.temperature <= 300):
        raise ValueError(
            "Hansen bangap expression used out of its nominal application range. "
            "temperature must be between 4K and 300K"
        )

    if not isinstance(detector, CMOS):
        raise TypeError("Expecting a 'CMOS' detector object.")

    signal_mean_array = detector.pixel.array.astype("float64")
    signal_non_linear = compute_physical_non_linearity(
        array_2d=signal_mean_array,
        temperature=detector.environment.temperature,
        fixed_capacitance=fixed_capacitance,
        v_bias=v_bias,
        cutoff=cutoff,
        n_acceptor=n_acceptor,
        n_donor=n_donor,
        diode_diameter=diode_diameter,
    )

    detector.signal.array = signal_non_linear


physical_non_linearity.meta = Metadata(
    name="physical_non_linearity",
    model_group="Charge Measurement",
    detector="CMOS",
    status=None,
    model=MetadataModel(
        description=r"""With this model you can add non-linearity to :py:class:`~pyxel.data_structure.Signal` array.

In this simplified analytical detector non-linearity model :cite:p:`pichon`
which assumes the detector is working far from saturation,
the current flowing in the diode is restricted to a photonic current:

:math:`\frac{dV}{dt}=\frac{-I_{ph}}{C}`.

The integrating capacitance can be written as a sum of fixed capacitance :math:`C_f` in the readout integrated circuit
and diode capacitance:

:math:`C=C_f+\frac{C_0}{1-\frac{V}{V_{bi}}}`,

The diode capacitance at 0 bias :math:`C_0` is :cite:p:`sze`:

:math:`C_0=A\sqrt{\frac{e\epsilon\epsilon_0}{2V_{bi}}(\frac{1}{N_a}+\frac{1}{N_d})}`.

:math:`A` is the area of the circular shaped diode, :math:`e` electron charge,
:math:`\epsilon` dielectric constant of the material,
and :math:`N_a` and :math:`N_d` are acceptor and donor concentrations.
:math:`V_{bi}` is the built-in diode potential and is a function of :math:`N_a`, :math:`N_d`,
temperature and intrinsic carrier concentration.
By inserting second equation into first equation and integrating,
one can express voltage on the detector after exposure as a solution of a quadratic equation.
Different to the non-linearity model presented in Plazas et al. (2017) :cite:p:`Plazas_2017`,
this model takes into account the additional fixed capacitance and the gain non-linearity.
Still it is not a complete physical model and does not simulate the saturation of the detector.
Additionally, it assumes a planar geometry of the diode instead of a cylindrical.""",
        config="""
- name: physical_non_linearity
  func: pyxel.models.charge_measurement.physical_non_linearity
  enabled: true
  arguments:
    cutoff: 2.1
    n_acceptor: 1.e+18
    n_donor: 3.e+15
    diode_diameter: 10.
    v_bias: 0.1
    fixed_capacitance: 5.e-15
""",
        notebooks=[
            ":external+pyxel_data:doc:`examples/models/non_linearity/non_linearity`"
        ],
        notes="This model is specific to the :term:`CMOS` detector.",
    ),
)


def compute_physical_non_linearity_with_saturation(
    signal_array_2d: np.ndarray,
    charge_array_2d: np.ndarray,
    time_step: float,
    step_number: int,
    temperature: float,
    cutoff: float,
    n_donor: float,
    n_acceptor: float,
    phi_implant: float,
    d_implant: float,
    saturation_current: float,
    ideality_factor: float,
    v_reset: float,
    d_sub: float,
    fixed_capacitance: float,
    euler_points: int,
) -> np.ndarray:
    """Compute physical non-linear signal with saturation.

    Parameters
    ----------
    signal_array_2d : ndarray
        Input signal array.
    charge_array_2d : ndarray
        Input photon array.
    time_step
        Time step. Unit: s.
    step_number : int
        Step number.
    temperature : float
        Temperature. Unit: K.
    cutoff : float
        Cutoff wavelength. unit: um.
    n_donor : float
        Donor density. Unit: atoms/cm^3.
    n_acceptor : float
        Acceptor density. Unit: atoms/cm^3.
    phi_implant : float
        Diameter of the implantation. Unit: um.
    d_implant : float
        Depth of the implamantation. Unit: um.
    saturation_current : float
        Saturation current: e-/s/pix..
    ideality_factor : float
        Ideality factor.
    v_reset : float
        VRESET. Unit: V.
    d_sub : float
        DSUB. Unit: V.
    fixed_capacitance : float
        Additional fixed capacitance. Unit: F.
    euler_points : int
        Number of points in the euler method.

    Returns
    -------
    ndarray
        Output array containing non-linear signal. Unit: V.
    """
    # Derivation of Cd concentration in the alloy,  it depends on cutoff wavelength and targeted operating temperature
    # Here we are considering the case where the detector is operated at its nominal temperature,
    # it might not be always the case
    e_g_targeted = 1.24 / cutoff  # cutoff is um and Eg in eV
    xcd = np.linspace(start=0.2, stop=0.6, num=1000)

    # targeted_operating_temperature = temperature
    e_g_calculated = hgcdte_bandgap(xcd, temperature)  # Expected bandgap
    index = np.where(e_g_calculated > e_g_targeted)[0][0]
    x_cd = xcd[index]  # Targeted cadmium concentration in the HgCdTe alloy
    # Calculate the effective bandgap value at the temperature at which simulations are performed.
    row, col = signal_array_2d.shape

    phi_implant = phi_implant * 1e-6  # in m
    d_implant = d_implant * 1e-6  # in m

    if step_number == 0:
        signal_array_2d = v_reset * np.ones((row, col))

    # detector.signal.array should be expressed in unit of mV. It is the bias at the gate of the pixel SFD ????
    det_polar = euler(
        time_step=time_step,
        nb_pts=euler_points,
        v_bias=np.ravel(signal_array_2d) - d_sub,
        phi_implant=phi_implant,
        d_implant=d_implant,
        n_acceptor=n_acceptor,
        n_donor=n_donor,
        x_cd=x_cd,
        temperature=temperature,
        photonic_current=np.ravel(charge_array_2d) / time_step,
        fixed_capacitance=fixed_capacitance,
        sat_current=saturation_current,
        n=ideality_factor,
    )

    array = np.reshape(det_polar + d_sub, (row, col))
    non_linear_signal = array.astype("float64")

    return non_linear_signal


def physical_non_linearity_with_saturation(
    detector: CMOS,
    cutoff: float,
    n_donor: float,
    n_acceptor: float,
    phi_implant: float,
    d_implant: float,
    saturation_current: float,
    ideality_factor: float,
    v_reset: float,
    d_sub: float,
    fixed_capacitance: float,
    euler_points: int,
) -> None:
    """Apply physical non-linearity with saturation.

    Parameters
    ----------
    detector : Detector
        Pyxel detector object.
    cutoff : float
        Cutoff wavelength. unit: um
    n_donor : float
        Donor density. Unit: atoms/cm^3
    n_acceptor : float
        Acceptor density. Unit: atoms/cm^3
    phi_implant : float
        Diameter of the implantation. Unit: um
    d_implant : float
        Depth of the implamantation. Unit: um
    saturation_current : float
        Saturation current: e-/s/pix.
    ideality_factor : float
        Ideality factor.
    v_reset : float
        VRESET. Unit: V.
    d_sub : float
        DSUB. Unit: V.
    fixed_capacitance : float
        Additional fixed capacitance. Unit: F.
    euler_points : int
        Number of points in the euler method.

    Notes
    -----
    For more information, you can find an example here:
    :external+pyxel_data:doc:`examples/models/non_linearity/non_linearity`.
    """
    if not (4 <= detector.environment.temperature <= 300):
        raise ValueError(
            "Hansen bangap expression used out of its nominal application range. "
            "temperature must be between 4K and 300K"
        )

    if not isinstance(detector, CMOS):
        raise TypeError("Expecting a 'CMOS' detector object.")

    if detector.is_first_readout:
        # This is the first step
        signal_2d = detector.signal.array
    else:
        signal_2d = np.array(detector.data["/non_linearity_with_saturation/previous"])

        if detector.is_last_readout:
            # This is the last step. Remove the previous value
            detector.data["/non_linearity_with_saturation"].orphan()

    signal_non_linear = compute_physical_non_linearity_with_saturation(
        signal_array_2d=signal_2d,
        charge_array_2d=detector.charge.array,
        time_step=detector.time_step,
        step_number=detector.pipeline_count,
        temperature=detector.environment.temperature,
        cutoff=cutoff,
        n_donor=n_donor,
        n_acceptor=n_acceptor,
        phi_implant=phi_implant,
        d_implant=d_implant,
        saturation_current=saturation_current,
        ideality_factor=ideality_factor,
        v_reset=v_reset,
        d_sub=d_sub,
        fixed_capacitance=fixed_capacitance,
        euler_points=euler_points,
    )

    if not detector.is_last_readout:
        # Update previous value
        detector.data["/non_linearity_with_saturation/previous"] = xr.DataArray(
            signal_non_linear,
            dims=["y", "x"],
            coords={
                "y": range(detector.geometry.row),
                "x": range(detector.geometry.col),
            },
        )

    detector.signal.array = signal_non_linear


physical_non_linearity_with_saturation.meta = Metadata(
    name="physical_non_linearity_with_saturation",
    model_group="Charge Measurement",
    detector="CMOS",
    status=None,
    authors=["Thibaut Pichon, CEA Saclay"],
    model=MetadataModel(
        description=r"""With this model you can add non-linearity to :py:class:`~pyxel.data_structure.Signal` array.

This model follows the description in :cite:p:`pichon` and gives the diode bias as a function of the time
by solving the following differential equation using the Euler method:

:math:`\frac{dV}{dt}=\frac{I(t)}{C(V)}`,

where :math:`V` is the applied bias, :math:`C` the node capacitance, and

:math:`I(t)=I_{sat}(exp(\frac{V}{nV_T})-1)-I_{ph}`.

:math:`I_{sat}` is the saturation current of the diode, :math:`V_T` is the thermal velocity,
:math:`n` is the ideality factor of the diode, and :math:`I_{ph}` is the photonic current.

Considering a diode with a cylindrical geometry, one can write

:math:`C(V)=C_f+\frac{a_0}{W_{dep}(V)}+b_0+c_0W_{dep}(V)`.

For an abrupt junction and diode dimension parameters :math:`\Phi_{imp}` and :math:`d_{imp}`,
following equations hold:

:math:`W_{dep}(V)=W_0(1-\frac{V}{V_{bi}})^{-\frac{1}{2}}`

:math:`a_0=(\frac{\Phi^2_{imp}}{4}+\Phi_{imp}d_{imp})\epsilon\pi`,

:math:`b_0=(\Phi_{imp}+d_{imp})2\epsilon\pi`,

:math:`c_0=3\epsilon\pi`.

User also specifies detector parameters ``v_reset`` and ``d_sub``.
This model assumes additional fixed capacitances,
the gain non-linearity is taken into account, it simulates the detector saturation and
assumes that the non-linearities observed mainly come from the PN junction diode.
""",
        config="""
- name: physical_non_linearity_with_saturation
  func: pyxel.models.charge_measurement.physical_non_linearity_with_saturation
  enabled: true
  arguments:
    cutoff: 2.1
    n_donor: 3.e+15
    n_acceptor: 1.e+18
    phi_implant: 6.e-6
    d_implant: 1.e-6
    saturation_current: 0.002
    ideality_factor: 1.34
    v_reset: 0.
    d_sub: 0.220
    fixed_capacitance: 5.e-15
    euler_points: 100
""",
        notes="This model is specific to the :term:`CMOS` detector.",
        notebooks=[
            ":external+pyxel_data:doc:`examples/models/non_linearity/non_linearity`"
        ],
    ),
)
