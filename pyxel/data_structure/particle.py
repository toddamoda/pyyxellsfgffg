#   --------------------------------------------------------------------------
#   Copyright 2018 SCI-FIV, ESA (European Space Agency)
#   --------------------------------------------------------------------------
"""Pyxel general particle class to track particles like photons, electrons, holes."""
# import numpy as np
import pandas as pd
# from astropy.units import cds
# cds.enable()


class Particle:
    """Class defining and storing information of all particles with their position, velocity, energy, etc."""

    def __init__(self) -> None:
        """TBW."""
        self.EMPTY_FRAME = pd.DataFrame()
        self.frame = pd.DataFrame()

    def get_values(self, quantity: str, id_list: list = None):
        """Get quantity values of particles defined with id_list. By default it returns values of all particles.

        :param quantity: name of quantity: ``number``, ``energy``, ``position_ver``, ``velocity_hor``, etc.
        :param id_list: list of particle ids: ``[0, 12, 321]``
        :return: array
        """
        if id_list:
            array = self.frame.query('index in %s' % id_list)[quantity].values
        else:
            array = self.frame[quantity].values
        return array

    def set_values(self, quantity: str, new_value_list: list, id_list: list = None):
        """Update quantity values of particles defined with id_list. By default it updates all.

        :param quantity: name of quantity: ``number``, ``energy``, ``position_ver``, ``velocity_hor``, etc.
        :param new_value_list: list of values ``[1.12, 2.23, 3.65]``
        :param id_list: list of particle ids: ``[0, 12, 321]``
        """
        new_df = pd.DataFrame({quantity: new_value_list}, index=id_list)
        self.frame.update(new_df)

    def remove(self, id_list: list = None):
        """Remove particles defined with id_list. By default it removes all particles from DataFrame.

        :param id_list: list of particle ids: ``[0, 12, 321]``
        """
        if id_list:
            self.frame.query('index not in %s' % id_list, inplace=True)
        else:
            self.frame = self.EMPTY_FRAME.copy()
