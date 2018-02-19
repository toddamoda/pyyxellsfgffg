#   --------------------------------------------------------------------------
#   Copyright 2018 SCI-FIV, ESA (European Space Agency)
#   --------------------------------------------------------------------------
"""PyXel! Pixel class to store and transfer charge packets inside detector."""
import numpy as np
import pandas as pd
# from astropy import units as u
from astropy.units import cds


cds.enable()


def round_convert_to_int(input_array: np.ndarray):
    """Round list of floats in numpy array and convert to integers
    Use on data before adding into DataFrame.

    :param input_array: numpy array object OR numpy array (float, int)
    :return:
    """
    array = input_array.astype(float)
    array = np.rint(array)
    array = array.astype(int)
    return array


def convert_to_int(input_array: np.ndarray):
    """Convert numpy array to integer
    Use on data after getting it from DataFrame.

    :param input_array: numpy array object OR numpy array (float, int)
    :return:
    """
    return input_array.astype(int)


class Pixel:
    """Pixel class defining and storing information of charge packets of all pixels with their properties
    like stored charge, position, lost charge."""

    def __init__(self,
                 detector):
        """TBW.

        :param detector:
        """
        self.detector = detector
        self.nextid = None
        self.frame = None
        self.__create_dataframe__()

    def __create_dataframe__(self):
        """TBW.

        :return:
        """
        self.nextid = 0
        self.frame = pd.DataFrame(columns=['id',
                                           'charge',
                                           'pixel_index_ver',
                                           'pixel_index_hor'])

    def generate_pixels(self):
        """Group charges into packets and fill pixel DataFrame"""
        charge_per_pixel = self.detector.charges.get_numbers()

        charge_pos_ver = self.detector.charges.get_positions_ver()
        charge_pos_hor = self.detector.charges.get_positions_hor()

        pixel_index_ver = np.floor_divide(charge_pos_ver, self.detector.geometry.pixel_vert_size).astype(int)
        pixel_index_hor = np.floor_divide(charge_pos_hor, self.detector.geometry.pixel_horz_size).astype(int)

        self.add_pixel(charge_per_pixel,
                       pixel_index_ver,
                       pixel_index_hor)

    def add_pixel(self,
                  charge,
                  pixel_index_ver,
                  pixel_index_hor):
        """Creating new pixel charge packet which is stored in a pandas DataFrame.

        :return:
        """

        if len(charge) == len(pixel_index_ver) == len(pixel_index_hor):
            elements = len(charge)
        else:
            raise ValueError('List arguments have different lengths')

        # Rounding and converting to integer
        charge = round_convert_to_int(charge)
        pixel_index_ver = round_convert_to_int(pixel_index_ver)
        pixel_index_hor = round_convert_to_int(pixel_index_hor)

        # dict
        new_pixel = {'id': range(self.nextid, self.nextid + elements),
                     'charge': charge,
                     'pixel_index_ver': pixel_index_ver,
                     'pixel_index_hor': pixel_index_hor}

        new_pixel_df = pd.DataFrame(new_pixel)
        self.nextid += elements

        # Adding new pixels to the DataFrame
        self.frame = pd.concat([self.frame, new_pixel_df], ignore_index=True)

    def generate_2d_charge_array(self):
        """Generating 2d numpy array from pixel DataFrame.

        :return:
        """
        charge_per_pixel = self.get_pixel_charges()
        pixel_index_ver = self.get_pixel_positions_ver()
        pixel_index_hor = self.get_pixel_positions_hor()

        charge_2d_array = np.zeros((self.detector.geometry.row, self.detector.geometry.col), dtype=float)
        charge_2d_array[pixel_index_ver, pixel_index_hor] = charge_per_pixel

        return convert_to_int(charge_2d_array)

    def update_from_2d_charge_array(self, array):
        """Recreate pixel DataFrame from a 2d numpy array.

        :return:
        """
        self.__create_dataframe__()

        row, col = array.shape
        if row != self.detector.geometry.row or col != self.detector.geometry.col:
            raise ValueError

        ver_index = list(range(0, row))
        hor_index = list(range(0, col))
        ver_index = np.repeat(ver_index, col)
        hor_index = np.tile(hor_index, row)

        self.add_pixel(array.flatten(), ver_index, hor_index)

    def get_pixel_charges(self, id_list='all'):
        """Get number of charges per pixel DataFrame row.

        :param id_list:
        :return:
        """
        if id_list == 'all':
            array = self.frame.charge.values
        else:
            array = self.frame.query('id in %s' % id_list).charge.values

        return convert_to_int(array)

    def get_pixel_positions_ver(self, id_list='all'):
        """Get vertical positions of pixels.

        :param id_list:
        :return:
        """
        if id_list == 'all':
            array = self.frame.pixel_index_ver.values
        else:
            array = self.frame.query('id in %s' % id_list).pixel_index_ver.values
        return convert_to_int(array)

    def get_pixel_positions_hor(self, id_list='all'):
        """Get horizontal positions of pixels.

        :param id_list:
        :return:
        """
        if id_list == 'all':
            array = self.frame.pixel_index_hor.values
        else:
            array = self.frame.query('id in %s' % id_list).pixel_index_hor.values
        return convert_to_int(array)

    # def change_all_charges(self, new_charge_list):
    #     """
    #     Update number of photons in each row
    #     :param new_charge_list:
    #     :return:
    #     """
    #     new_df = pd.DataFrame({'charge': new_charge_list})
    #     self.frame.update(new_df)
    #     # TODO: update all rows with given ids in list (id_list can be a 2nd optional arg)
    #     # https://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.update.html
