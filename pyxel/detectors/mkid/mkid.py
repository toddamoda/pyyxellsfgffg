#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.
#
#
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

""":term:`MKID`-array detector modeling class."""

from collections.abc import Mapping
from typing import TYPE_CHECKING

from pyxel.data_structure import Phase
from pyxel.detectors import Detector
from pyxel.util import memory_usage_details

if TYPE_CHECKING:
    import pandas as pd

    from pyxel.detectors import Characteristics, Environment, MKIDGeometry


class MKID(Detector):
    """:term:`MKID`-based detector class containing all detector attributes and data."""

    def __init__(
        self,
        geometry: "MKIDGeometry",
        environment: "Environment",
        characteristics: "Characteristics",
    ):
        self._geometry: MKIDGeometry = geometry
        self._characteristics: Characteristics = characteristics

        super().__init__(environment=environment)
        self.reset()

    def __eq__(self, other) -> bool:
        return (
            type(self) is type(other)
            and self.geometry == other.geometry
            and self.environment == other.environment
            and self.characteristics == other.characteristics
            and self._phase == other._phase
            and super().__eq__(other)
        )

    def reset(self) -> None:
        """TBW."""
        super().reset()
        self._phase = Phase(geo=self.geometry)

    def empty(self, empty_all: bool = True) -> None:
        """Empty the data in the detector.

        Returns
        -------
        None
        """
        super().empty(empty_all)

        if empty_all and self._phase:
            self.phase.array *= 0

    @property
    def geometry(self) -> "MKIDGeometry":
        """TBW."""
        return self._geometry

    @property
    def characteristics(self) -> "Characteristics":
        """TBW."""
        return self._characteristics

    @property
    def phase(self) -> Phase:
        """TBW."""
        if not self._phase:
            raise RuntimeError("'phase' not initialized.")

        return self._phase

    def memory_usage(
        self, print_result: bool = True, human_readable: bool = True
    ) -> dict:
        """TBW.

        Returns
        -------
        dict
            Dictionary of attribute memory usage
        """
        attributes = [
            "_photon",
            "_charge",
            "_pixel",
            "_signal",
            "_image",
            "_phase",
            "material",
            "environment",
            "_geometry",
            "_characteristics",
        ]

        return memory_usage_details(
            self, attributes, print_result=print_result, human_readable=human_readable
        )

    # TODO: Refactor this
    def to_dict(self) -> Mapping:
        """Convert an instance of `MKID` to a `dict`."""
        dct = {
            "version": 1,
            "type": "MKID",
            "properties": {
                "geometry": self.geometry.to_dict(),
                "environment": self.environment.to_dict(),
                "characteristics": self.characteristics.to_dict(),
            },
            "data": {
                "photon": None if self._photon is None else self._photon.array.copy(),
                "pixel": None if self._pixel is None else self._pixel.array.copy(),
                "signal": None if self._signal is None else self._signal.array.copy(),
                "image": None if self._image is None else self._image.array.copy(),
                "phase": None if self._phase is None else self._phase.array.copy(),
                "data": None if self._data is None else self._data.to_dict(),
                "charge": (
                    None
                    if self._charge is None
                    else {
                        "array": self._charge.array.copy(),
                        "frame": self._charge.frame.copy(),
                    }
                ),
                "scene": (
                    None
                    if self._scene is None
                    else {
                        key.replace("/", "#"): value
                        for key, value in self._scene.to_dict().items()
                    }
                ),
            },
        }

        return dct

    # TODO: Refactor this
    @classmethod
    def from_dict(cls, dct: Mapping) -> "MKID":
        """Create a new instance of `MKID` from a `dict`."""
        # TODO: This is a simplistic implementation. Improve this.
        import numpy as np
        import xarray as xr
        from datatree import DataTree

        from pyxel.data_structure import Scene
        from pyxel.detectors import Characteristics, Environment, MKIDGeometry

        if dct["type"] != "MKID":
            raise ValueError

        if dct["version"] != 1:
            raise ValueError

        properties = dct["properties"]
        geometry = MKIDGeometry.from_dict(properties["geometry"])
        environment = Environment.from_dict(properties["environment"])
        characteristics = Characteristics.from_dict(properties["characteristics"])

        detector = cls(
            geometry=geometry,
            environment=environment,
            characteristics=characteristics,
        )

        data = dct["data"]

        if "photon" in data:
            detector.photon.array = np.asarray(data["photon"])

        if "pixel" in data:
            detector.pixel.array = np.asarray(data["pixel"])
        if "signal" in data:
            detector.signal.array = np.asarray(data["signal"])
        if "image" in data:
            detector.image.array = np.asarray(data["image"])
        if "data" in data:
            detector._data = DataTree.from_dict(
                {
                    key: xr.Dataset.from_dict(value)
                    for key, value in data["data"].items()
                }
            )
        if "scene" in data and (scene_dct := data["scene"]) is not None:
            detector.scene = Scene.from_dict(
                {key.replace("#", "/"): value for key, value in scene_dct.items()}
            )
        if "charge" in data and data["charge"] is not None:
            charge_dct = data["charge"]
            detector.charge._array = np.asarray(charge_dct["array"])

            new_frame: pd.DataFrame = charge_dct["frame"]
            previous_frame: pd.DataFrame = detector.charge._frame
            detector.charge._frame = new_frame[previous_frame.columns]

        return detector


"""
.......... From https://github.com/sahderooij/
"""


class Superconductor(object):
    '''General class for superconductor material properties.
    Free electron model is assumed.'''

    def __init__(self, name, Tc, TD, N0, rhon, kF,  t0, tpb, cT, cL, rho):
        self.name = name
        self.kbTc = Tc * const.Boltzmann / const.e * 1e6  # critical Temperature in µeV
        self.kbTD = TD * const.Boltzmann / const.e * 1e6  # Debye Energy in µeV
        self.N0 = N0  # Electronic DoS at Fermi Surface [µeV^-1 µm^-3]
        self.rhon = rhon  # normal state resistivity [µOhmcm] (!)
        self.kF = kF  # Fermi wave number [µm^-1]
        self.t0 = t0  # electron-phonon interaction time [µs]
        self.tpb = tpb  # phonon pair-breaking time [µs]
        self.cT = cT # transverse speed of sound
        self.cL = cL # longitudinal speed of sound
        self.rho = rho/const.e*1e-12 # mass density give in kg/m^3, returns in µeV/(µm/µs)**2 µm^-3
        
    @property
    def mstar(self):
        '''effective electron mass in µeV/(µm/µs)^2'''
        return 2 * (const.hbar*1e12/const.e)**2 * self.N0 * np.pi**2/self.kF
        
    @property
    def vF(self):
        '''Fermi velocity in µm/µs'''
        return const.hbar*1e12/const.e * self.kF / self.mstar
    
    @property
    def EF(self):
        '''Fermi energy in µeV'''
        return (const.hbar*1e12/const.e)**2 * self.kF**2 / (2*self.mstar)
    
    @property
    def l_e(self):
        '''electron mean free path in µm'''
        return (3*np.pi**2 * (const.hbar *1e12 / const.e) /
                (self.kF**2 * (self.rhon * 1e10 / const.e) * const.e**2))

    @property
    def lbd0(self):
        """London penetration depth (i.e. at T = 0 K) in µm. 
        This only holds when Mattis-Bardeen can be used 
        (i.e. dirty limit or extreme anomalous limit)"""
        return np.sqrt(
            const.hbar * 1e12 / const.e
            * self.rhon * 1e4
            / (const.mu_0 * 1e6
               * self.D0
               * np.pi)
        )

    @property
    def Vsc(self):
        """Calculates the superconducting coupling strength in BSC-theory 
        from the BSC relation 2D=3.52kbTc."""

        def integrand1(E, D):
            return 1 / np.sqrt(E ** 2 - D ** 2)

        return 1 / (
            integrate.quad(integrand1, self.D0, self.kbTD,
                           args=(self.D0,))[0] * self.N0
        )

    @property
    def Ddata(self):
        """To speed up the calculation for Delta, an interpolation of generated values is used.
        Ddata_{SC}_{Tc}.npy contains this data, where a new one is needed 
        for each superconductor (SC) and crictical temperature (Tc).
        This function returns the Ddata array."""

        Ddataloc = os.path.dirname(__file__) + "/Ddata/"
        if self.name != "":
            Tc = str(
                np.around(self.kbTc / (const.Boltzmann / const.e * 1e6), 3)
            ).replace(".", "_")
            try:
                Ddata = np.load(Ddataloc + f"Ddata_{self.name}_{Tc}.npy")
            except FileNotFoundError:
                Ddata = None
        else:
            Ddata = None
        return Ddata

    @property
    def D0(self):
        """BSC relation"""
        return 1.76 * self.kbTc

    @property
    def xi0(self):
        """BSC Coherence length at T = 0 K (in [µm])"""
        return const.hbar * 1e12 / const.e * self.vF / (np.pi * self.D0)
    
    @property
    def xi_DL(self):
        '''Dirty limit coherence length'''
        if self.xi0/self.l_e > 10:  
            return np.sqrt(self.xi0 * self.l_e)
        else:
            warnings.warn(f'Not in dirty limit xi0={self.xi0}, l={self.l}')

    @property
    def jc(self):
        """Critical current density, in A/µm^2, from Romijn1982"""
        return .75*np.sqrt(
            self.N0 * self.D0**3 /
            (self.rhon * 1e-2 / const.e * const.hbar * 1e12 / const.e)
                           )
    
    @property
    def D(self):
        '''Diffusion constant in µm^2/µs'''
        return 1/(2 * (self.rhon * 1e10 / const.e) * const.e**2 * self.N0)
    
    @property
    def lbd_eph(self):
        '''Electron-phonon coupling constant, (with BSC relation 2D=3.52kbTc)'''
        return (self.N0 * self.Vsc)
        
    @property
    def rhoM(self):
        '''The Mott resisitivty in µOhm cm'''
        return 3 * np.pi**2 * const.hbar / (const.e**2 * self.kF * 1e6) * 1e8
    
    @property
    def cs(self):
        '''effective 3D speed of sound'''
        return (3/(2/self.cT**3 + 1/self.cL**3))**(1/3)


Al = Superconductor('Al', 
                     Tc=1.2,
                     rhon=0.9,
                     TD=433,
                     N0=1.72e4,
                     kF=1.75e4,
                     t0=0.44, 
                     tpb=0.28e-3,
                     cL=6.65e3,
                     cT=3.26e3,
                     rho=2.5e3)
