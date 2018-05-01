#   --------------------------------------------------------------------------
#   Copyright 2018 SCI-FIV, ESA (European Space Agency)
#   --------------------------------------------------------------------------
"""PyXel! Pixel class to store and transfer charge packets inside detector."""
import numpy as np
import pandas as pd
# from astropy import units as u
from astropy.units import cds

from pyxel import util

cds.enable()


class Pixel:
    """Pixel class defining and storing information of charge packets.

    Pixel properties stored are: charge, position, lost charge.
    """

    def __init__(self,
                 detector):
        """TBW.

        :param detector:
        """
        self.detector = detector
        self.pixel_array = None
        self.fill_pixels_with_charges()

        # self.nextid = None
        # self.frame = None
        # self.__create_dataframe__()

    # def __create_dataframe__(self):
    #     """TBW.
    #
    #     :return:
    #     """
    #     self.nextid = 0
    #     geo = self.detector.geometry
    #     elements = geo.row * geo.col
    #
    #     pixel_index_ver = list(range(0, geo.row))
    #     pixel_index_hor = list(range(0, geo.col))
    #     pixel_index_ver = np.repeat(pixel_index_ver, geo.col)
    #     pixel_index_hor = np.tile(pixel_index_hor, geo.row)
    #
    #     # dict
    #     new_pixel = {'id': range(self.nextid, self.nextid + elements),
    #                  'charge': [0.] * elements,
    #                  'pixel_index_ver': pixel_index_ver,
    #                  'pixel_index_hor': pixel_index_hor}
    #
    #     self.frame = pd.DataFrame(new_pixel)
    #     self.frame = self.frame.set_index("id")

    def fill_pixels_with_charges(self):
        """Group charges into packets and fill pixel DataFrame."""
        charge_per_pixel = self.detector.charges.get_numbers()

        charge_pos_ver = self.detector.charges.get_positions_ver()
        charge_pos_hor = self.detector.charges.get_positions_hor()

        pixel_index_ver = np.floor_divide(charge_pos_ver, self.detector.geometry.pixel_vert_size).astype(int)
        pixel_index_hor = np.floor_divide(charge_pos_hor, self.detector.geometry.pixel_horz_size).astype(int)

        self.pixel_array = np.zeros((self.detector.geometry.row, self.detector.geometry.col), dtype=float)

        for i in range(len(charge_per_pixel)):
            self.pixel_array[pixel_index_ver[i], pixel_index_hor[i]] += charge_per_pixel[i]

        # return util.convert_to_int(charge_2d_array)

        # self.add_charge_to_pixel(charge_per_pixel,
        #                          pixel_index_ver,
        #                          pixel_index_hor)

    # def add_charge_to_pixel(self,
    #                         new_charge,
    #                         pixel_index_ver,
    #                         pixel_index_hor):
    #     """Create new pixel charge packet which is stored in a pandas DataFrame.
    #
    #     :return:
    #     """
    #     if len(new_charge) == len(pixel_index_ver) == len(pixel_index_hor):
    #         elements = len(new_charge)
    #     else:
    #         raise ValueError('List arguments have different lengths')

        # index_charge = self.frame[(self.frame.pixel_index_ver == 0) & (self.frame.pixel_index_hor == 1)].index
        #
        # index_charge2 = self.frame.loc[(self.frame['pixel_index_ver'] == 0) &
        #                                (self.frame['pixel_index_hor'] == 1)].index

        # index_charge = self.frame[self.frame['pixel_index_ver'].isin(pixel_index_ver) &
        #                           (self.frame.pixel_index_hor == pixel_index_hor[0])].index
        # index_charge = self.frame[self.frame['pixel_index_hor'].isin(pixel_index_hor) &
        #                           (self.frame.pixel_index_ver == pixel_index_ver[0])].index
        #
        # index_charge = []
        # asd = iter(pixel_index_ver)
        # index_charge += self.frame[self.frame['pixel_index_hor'].isin(pixel_index_hor) &
        #                            (self.frame.pixel_index_ver == asd.__next__())].index

        # index_charge2 = self.frame.loc[self.frame['pixel_index_ver'].isin(iter([0, 1, 2])) &
        #                                (self.frame['pixel_index_hor'] == 1)].index

    #  def add_pixel(self,
    #               charge,
    #               pixel_index_ver,
    #               pixel_index_hor):
    #     """Create new pixel charge packet which is stored in a pandas DataFrame.
    #
    #     :return:
    #     """
    #     if len(charge) == len(pixel_index_ver) == len(pixel_index_hor):
    #         elements = len(charge)
    #     else:
    #         raise ValueError('List arguments have different lengths')
    #
    #     # Rounding and converting to integer
    #     # charge = util.round_convert_to_int(charge)
    #     pixel_index_ver = util.round_convert_to_int(pixel_index_ver)
    #     pixel_index_hor = util.round_convert_to_int(pixel_index_hor)
    #
    #     # TODO we need to merge the charges within the same pixels!!!!!!!!!!!!!!!!!!!!!!
    #
    #     # dict
    #     new_pixel = {'id': range(self.nextid, self.nextid + elements),
    #                  'charge': charge,
    #                  'pixel_index_ver': pixel_index_ver,
    #                  'pixel_index_hor': pixel_index_hor}
    #
    #     new_pixel_df = pd.DataFrame(new_pixel)
    #     self.nextid += elements
    #
    #     # Adding new pixels to the DataFrame
    #     self.frame = pd.concat([self.frame, new_pixel_df], ignore_index=True)
    #
    # def add_empty_pixels(self):
    #     """Create new empty pixel DataFrame.
    #
    #     :return:
    #     """
    #     geo = self.detector.geometry
    #     pixel_index_ver = range(geo.row)
    #     pixel_index_hor = range(geo.col)
    #
    #     # TODO we need to merge the charges within the same pixels!!!!!!!!!!!!!!!!!!!!!!
    #
    #     elements = geo.row * geo.col
    #     dict
    #     new_pixel = {'id': range(self.nextid, self.nextid + elements),
    #                  'charge': [0.] * elements,
    #                  'pixel_index_ver': pixel_index_ver,
    #                  'pixel_index_hor': pixel_index_hor}
    #
    #     new_pixel_df = pd.DataFrame(new_pixel)
    #     # self.nextid += elements
    #
    #     # Adding new pixels to the DataFrame
    #     self.frame = pd.concat([self.frame, new_pixel_df], ignore_index=True)

    # def generate_2d_charge_array(self):
    #     """Generate 2d numpy array from pixel DataFrame.
    #
    #     :return:
    #     """
    #     charge_per_pixel = self.get_pixel_charges()
    #     pixel_index_ver = self.get_pixel_positions_ver()
    #     pixel_index_hor = self.get_pixel_positions_hor()
    #
    #     charge_2d_array = np.zeros((self.detector.geometry.row, self.detector.geometry.col), dtype=float)
    #     charge_2d_array[pixel_index_ver, pixel_index_hor] = charge_per_pixel
    #
    #     # return util.convert_to_int(charge_2d_array)
    #     return charge_2d_array
    #
    # def update_from_2d_charge_array(self, array):
    #     """Recreate pixel DataFrame from a 2d numpy array.
    #
    #     :return:
    #     """
    #     self.__create_dataframe__()
    #
    #     row, col = array.shape
    #     if row != self.detector.geometry.row or col != self.detector.geometry.col:
    #         raise ValueError
    #
    #     ver_index = list(range(0, row))
    #     hor_index = list(range(0, col))
    #     ver_index = np.repeat(ver_index, col)
    #     hor_index = np.tile(hor_index, row)
    #
    #     self.add_charge_to_pixel(array.flatten(), ver_index, hor_index)
    #
    # def get_pixel_charges(self, id_list='all'):
    #     """Get number of charges per pixel DataFrame row.
    #
    #     :param id_list:
    #     :return:
    #     """
    #     if id_list == 'all':
    #         array = self.frame.charge.values
    #     else:
    #         array = self.frame.query('id in %s' % id_list).charge.values
    #
    #     # return util.convert_to_int(array)
    #     return array
    #
    # def get_pixel_positions_ver(self, id_list='all'):
    #     """Get vertical positions of pixels.
    #
    #     :param id_list:
    #     :return:
    #     """
    #     if id_list == 'all':
    #         array = self.frame.pixel_index_ver.values
    #     else:
    #         array = self.frame.query('id in %s' % id_list).pixel_index_ver.values
    #     return util.convert_to_int(array)
    #
    # def get_pixel_positions_hor(self, id_list='all'):
    #     """Get horizontal positions of pixels.
    #
    #     :param id_list:
    #     :return:
    #     """
    #     if id_list == 'all':
    #         array = self.frame.pixel_index_hor.values
    #     else:
    #         array = self.frame.query('id in %s' % id_list).pixel_index_hor.values
    #     return util.convert_to_int(array)

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
