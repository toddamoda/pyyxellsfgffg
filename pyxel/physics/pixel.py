#   --------------------------------------------------------------------------
#   Copyright 2018 SCI-FIV, ESA (European Space Agency)
#   --------------------------------------------------------------------------
"""
PyXel! Pixel class to store and transfer charge packets inside detector
"""
import numpy as np
# from astropy import units as u
from astropy.units import cds
import pandas as pd

cds.enable()


class Pixel:
    """
    Pixel class defining and storing information of charge packets of all pixels with their properties
    like stored charge, position, lost charge
    """

    def __init__(self,
                 detector=None):

        self.detector = detector
        self.nextid = 0
        self.frame = pd.DataFrame(columns=['id',
                                           'charge',
                                           'pixel_index_ver',
                                           'pixel_index_hor'])

    def generate_pixels(self):
        """
        Group charges into packets and fill pixel DataFrame
        """
        charge_per_pixel = self.detector.charges.get_numbers()

        charge_pos_ver = self.detector.charges.get_positions_ver()
        charge_pos_hor = self.detector.charges.get_positions_hor()

        pixel_index_ver = np.floor_divide(charge_pos_ver, self.detector.pix_vert_size).astype(int)
        pixel_index_hor = np.floor_divide(charge_pos_hor, self.detector.pix_horz_size).astype(int)

        self.add_pixel(charge_per_pixel,
                       pixel_index_ver,
                       pixel_index_hor)

    def generate_signal(self):
        """
        Read output signal of detector pixels as a 2d numpy array, unit: Volts
        :return:
        """
        charge_per_pixel = self.get_pixel_charges()
        pixel_index_ver = self.get_pixel_positions_ver()
        pixel_index_hor = self.get_pixel_positions_hor()

        signal_2d_array = np.zeros((self.detector.row, self.detector.col), dtype=float)
        signal_2d_array[pixel_index_ver, pixel_index_hor] = charge_per_pixel

        return signal_2d_array

    def add_pixel(self,
                  charge,
                  pixel_index_ver,
                  pixel_index_hor):
        """
        Creating new pixel charge packet which is stored in a pandas DataFrame
        :return:
        """

        if len(charge) == len(pixel_index_ver) == len(pixel_index_hor):
            elements = len(charge)
        else:
            raise ValueError('List arguments have different lengths')

        # dict
        new_pixel = {'id': range(self.nextid, self.nextid + elements),
                     'charge': charge,
                     'pixel_index_ver': pixel_index_ver,
                     'pixel_index_hor': pixel_index_hor}

        new_pixel_df = pd.DataFrame(new_pixel)
        self.nextid = self.nextid + elements

        # Adding new pixels to the DataFrame
        self.frame = pd.concat([self.frame, new_pixel_df], ignore_index=True)

    def get_pixel_charges(self, id_list='all'):
        """
        Get number of charges per pixel DataFrame row
        :param id_list:
        :return:
        """
        if id_list == 'all':
            array = self.frame.charge.values
        else:
            array = self.frame.query('id in %s' % id_list).charge.values
        return array.astype(int)

    def get_pixel_positions_ver(self, id_list='all'):
        """
        Get vertical positions of pixels
        :param id_list:
        :return:
        """
        if id_list == 'all':
            array = self.frame.pixel_index_ver.values
        else:
            array = self.frame.query('id in %s' % id_list).pixel_index_ver.values
        return array.astype(int)

    def get_pixel_positions_hor(self, id_list='all'):
        """
        Get horizontal positions of pixels
        :param id_list:
        :return:
        """
        if id_list == 'all':
            array = self.frame.pixel_index_hor.values
        else:
            array = self.frame.query('id in %s' % id_list).pixel_index_hor.values
        return array.astype(int)

    def change_all_charges(self, new_charge_list):
        """
        Update number of photons in each row
        :param new_charge_list:
        :return:
        """
        new_df = pd.DataFrame({'charge': new_charge_list})
        self.frame.update(new_df)
        # TODO: update all rows with given ids in list (id_list can be a 2nd optional arg)
        # https://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.update.html
