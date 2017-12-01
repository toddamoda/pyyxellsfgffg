""" Utility functions. """
from pathlib import Path


def get_data_dir(file_name=''):
    path_out = Path(__file__).parents[2].joinpath('data')
    if file_name:
        path_out = path_out.joinpath(file_name)
    return path_out
