"""
arCTIc (AlgoRithm for Charge Transfer Inefficiency Correction) is a program that can create or remove image trails
due to CTI, which is simulated via the modelling of trapping, releasing and the movement of charge along the pixels
inside a CCD.

Developed by James Nightingale, Richard Massey and Jacob Kegerris (University of Durham)
More information:
https://pypi.org/project/arcticpy/
"""

import typing as t
from copy import deepcopy

import arcticpy as ac
import numpy as np
from arcticpy.ccd import CCD
from arcticpy.roe import ROE, ROETrapPumping
from arcticpy.trap_managers import AllTrapManager
from autoarray.structures import frames
from numba import njit


# From 'cy_watermark_index_above_cloud_from_cloud_fractional_volume'
# in 'arcticpy/trap_managers_utils.pyx'
@njit
def numba_watermark_index_above_cloud_from_cloud_fractional_volume(
    cloud_fractional_volume,
    watermarks,
    max_watermark_index,
):

    total = 0.0

    index = watermarks.shape[0]

    for i in range(watermarks.shape[0]):
        total += watermarks[i, 0]
        if cloud_fractional_volume <= total:
            index = min(index, i)

    if total < cloud_fractional_volume:
        return max_watermark_index + 1
    else:
        return index


# From 'TrapManager.watermark_index_above_cloud_from_cloud_fractional_volume'
# in 'arcticpy/trap_manager.py'
# self => TrapManager object
@njit
def watermark_index_above_cloud_from_cloud_fractional_volume(
    # self,
    cloud_fractional_volume,
    watermarks,
    max_watermark_index,
):

    if cloud_fractional_volume == 0:
        return -1
    else:
        return numba_watermark_index_above_cloud_from_cloud_fractional_volume(
            cloud_fractional_volume, watermarks, max_watermark_index
        )


# From 'TrapManager.collapse_redundant_watermarks'
# in 'arcticpy/trap_manager.py'
# self => TrapManager object
@njit
def collapse_redundant_watermarks(
    # self,
    filled_watermark_value,  # from 'self'
    watermarks,
    watermarks_copy=None,
):
    # if watermarks_copy is None:
    #     do_copy = False
    #     # watermarks_copy = np.zeros_like(watermarks)
    # else:
    #     do_copy = True
    assert watermarks_copy is not None
    do_copy = True

    # Number of trap species
    num_traps = watermarks.shape[1] - 1
    assert num_traps == 1

    # Find the first watermark that is not completely filled for all traps
    watermark_index_not_filled = min(
        [
            np.argmax(watermarks[:, 1 + i_trap] != filled_watermark_value)
            for i_trap in range(num_traps)
        ]
    )

    # Skip if none or only one are completely filled
    if watermark_index_not_filled <= 1:
        if do_copy:
            return watermarks, watermarks_copy
        else:
            return watermarks

    # Total fractional volume of filled watermarks
    fractional_volume_filled = np.sum(watermarks[:watermark_index_not_filled, 0])

    # Combined fill values
    if do_copy:
        # Multiple trap species
        # if 1 < num_traps:
        #     axis = 1
        # else:
        #     axis = None
        # copy_fill_values = (
        #     np.sum(
        #         watermarks_copy[:watermark_index_not_filled, 0]
        #         * watermarks_copy[:watermark_index_not_filled, 1:].T,
        #         axis=axis,
        #     )
        #     / np.sum(watermarks_copy[:watermark_index_not_filled, 0])
        # )
        assert not (1 < num_traps)
        copy_fill_values = np.sum(
            watermarks_copy[:watermark_index_not_filled, 0]
            * watermarks_copy[:watermark_index_not_filled, 1:].T
        ) / np.sum(watermarks_copy[:watermark_index_not_filled, 0])

    # Remove the no-longer-needed overwritten watermarks
    watermarks[:watermark_index_not_filled, :] = 0
    if do_copy:
        watermarks_copy[:watermark_index_not_filled, :] = 0

    # Move the no-longer-needed watermarks to the end of the list
    # watermarks = np.roll(watermarks, 1 - watermark_index_not_filled, axis=0)
    _, watermarks_num_x = watermarks.shape
    watermarks = np.roll(
        watermarks, (1 - watermark_index_not_filled) * watermarks_num_x
    )

    if do_copy:
        # watermarks_copy = np.roll(
        #     watermarks_copy, 1 - watermark_index_not_filled, axis=0
        # )
        _, watermarks_copy_num_x = watermarks_copy.shape
        watermarks_copy = np.roll(
            watermarks_copy, (1 - watermark_index_not_filled) * watermarks_copy_num_x
        )

    # Edit the new first watermark
    watermarks[0, 0] = fractional_volume_filled
    watermarks[0, 1:] = filled_watermark_value
    if do_copy:
        watermarks_copy[0, 0] = fractional_volume_filled
        watermarks_copy[0, 1:] = copy_fill_values

    if do_copy:
        return watermarks, watermarks_copy
    else:
        return watermarks


# From 'TrapManager.collapse_redundant_watermarks'
# in 'arcticpy/trap_manager.py'
# self => TrapManager object
@njit
def collapse_redundant_watermarks_no_copy(
    # self,
    filled_watermark_value,  # from 'self'
    watermarks,
    # watermarks_copy=None,
):
    # if watermarks_copy is None:
    #     do_copy = False
    #     # watermarks_copy = np.zeros_like(watermarks)
    # else:
    #     do_copy = True
    # assert watermarks_copy is not None
    do_copy = False

    # Number of trap species
    num_traps = watermarks.shape[1] - 1
    assert num_traps == 1

    # Find the first watermark that is not completely filled for all traps
    watermark_index_not_filled = min(
        [
            np.argmax(watermarks[:, 1 + i_trap] != filled_watermark_value)
            for i_trap in range(num_traps)
        ]
    )

    # Skip if none or only one are completely filled
    if watermark_index_not_filled <= 1:
        # if do_copy:
        #     return watermarks, watermarks_copy
        # else:
        #     return watermarks
        return watermarks

    # Total fractional volume of filled watermarks
    fractional_volume_filled = np.sum(watermarks[:watermark_index_not_filled, 0])

    # Combined fill values
    # if do_copy:
    #     # Multiple trap species
    #     # if 1 < num_traps:
    #     #     axis = 1
    #     # else:
    #     #     axis = None
    #     # copy_fill_values = (
    #     #     np.sum(
    #     #         watermarks_copy[:watermark_index_not_filled, 0]
    #     #         * watermarks_copy[:watermark_index_not_filled, 1:].T,
    #     #         axis=axis,
    #     #     )
    #     #     / np.sum(watermarks_copy[:watermark_index_not_filled, 0])
    #     # )
    #     assert not (1 < num_traps)
    #     copy_fill_values = np.sum(
    #         watermarks_copy[:watermark_index_not_filled, 0]
    #         * watermarks_copy[:watermark_index_not_filled, 1:].T
    #     ) / np.sum(watermarks_copy[:watermark_index_not_filled, 0])

    # Remove the no-longer-needed overwritten watermarks
    watermarks[:watermark_index_not_filled, :] = 0
    # if do_copy:
    #     watermarks_copy[:watermark_index_not_filled, :] = 0

    # Move the no-longer-needed watermarks to the end of the list
    # watermarks = np.roll(watermarks, 1 - watermark_index_not_filled, axis=0)
    _, watermarks_num_x = watermarks.shape
    watermarks = np.roll(
        watermarks, (1 - watermark_index_not_filled) * watermarks_num_x
    )

    # if do_copy:
    #     # watermarks_copy = np.roll(
    #     #     watermarks_copy, 1 - watermark_index_not_filled, axis=0
    #     # )
    #     _, watermarks_copy_num_x = watermarks_copy.shape
    #     watermarks_copy = np.roll(
    #         watermarks_copy, (1 - watermark_index_not_filled) * watermarks_copy_num_x
    #     )

    # Edit the new first watermark
    watermarks[0, 0] = fractional_volume_filled
    watermarks[0, 1:] = filled_watermark_value
    # if do_copy:
    #     watermarks_copy[0, 0] = fractional_volume_filled
    #     watermarks_copy[0, 1:] = copy_fill_values

    # if do_copy:
    #     return watermarks, watermarks_copy
    # else:
    #     return watermarks
    return watermarks


# From 'TrapManager.fill_probabilities_from_dwell_time'
# in 'arcticpy/trap_manager.py'
# self => TrapManager object@njit
def fill_probabilities_from_dwell_time(
    # self,
    total_rates,  # from 'self'
    capture_rates,  # from 'self'
    emission_rates,  # from 'self'
    dwell_time,
):

    # Common factor for capture and release probabilities
    exponential_factor = (1 - np.exp(-total_rates * dwell_time)) / total_rates

    # New fill fraction for empty traps (Eqn. 20)
    # Ignore unnecessary warning from instant capture
    # with warnings.catch_warnings():
    #     warnings.filterwarnings(
    #         "ignore", message="invalid value encountered in multiply"
    #     )
    #     fill_probabilities_from_empty = self.capture_rates * exponential_factor

    fill_probabilities_from_empty = capture_rates * exponential_factor

    # Fix for instant capture
    fill_probabilities_from_empty[np.isnan(fill_probabilities_from_empty)] = 1

    # New fill fraction for filled traps (Eqn. 21)
    fill_probabilities_from_full = 1 - emission_rates * exponential_factor

    # New fill fraction from only release
    fill_probabilities_from_release = np.exp(-emission_rates * dwell_time)

    return (
        fill_probabilities_from_empty,
        fill_probabilities_from_full,
        fill_probabilities_from_release,
    )


# From 'cy_value_in_cumsum'
# in 'arcticpy/trap_managers_utils.pyx'
@njit
def value_in_cumsum(value, arr):
    total = arr[0]

    for i in range(1, arr.shape[0], 1):
        if value == total:
            return 1
        total += arr[i]

    if value == total:
        return 1
    else:
        return 0


# Function used in _n_electrons_released_and_captured_cloud_below_watermarks
@njit
def my_operation(
    arr,
    watermark_index_above_cloud,
    max_watermark_index,
    fill_probabilities_from_release,
):
    # self.watermarks[
    #     watermark_index_above_cloud + 1 : max_watermark_index + 1, 1:
    # ] *= fill_probabilities_from_release
    arr[
        watermark_index_above_cloud + 1 : max_watermark_index + 1, 1:
    ] *= fill_probabilities_from_release


# From 'TrapManager._n_electrons_released_and_captured__cloud_below_watermarks'
# in 'arcticpy/trap_manager.py'
# self => TrapManager object
def _n_electrons_released_and_captured_cloud_below_watermarks(
    self,
    n_free_electrons,
    cloud_fractional_volume,
    watermarks_initial,
    watermark_index_above_cloud,
    max_watermark_index,
    fill_probabilities_from_release,
    n_trapped_electrons_initial,
    ccd_filling_function,
):
    # Create the new watermark at the cloud fractional volume
    if cloud_fractional_volume > 0 and not value_in_cumsum(
        cloud_fractional_volume, self.watermarks[:, 0]
    ):
        # Update the watermark volumes, duplicated for the initial watermarks
        self.watermarks = numba_update_watermark_volumes_for_cloud_below_highest(
            watermarks=self.watermarks,
            cloud_fractional_volume=cloud_fractional_volume,
            watermark_index_above_cloud=watermark_index_above_cloud,
        )
        watermarks_initial = numba_update_watermark_volumes_for_cloud_below_highest(
            watermarks=watermarks_initial,
            cloud_fractional_volume=cloud_fractional_volume,
            watermark_index_above_cloud=watermark_index_above_cloud,
        )

        # Increment the index now that an extra watermark has been set
        max_watermark_index += 1

    # Release electrons from existing watermark levels above the cloud
    # Update the fill fractions
    # self.watermarks[
    #     watermark_index_above_cloud + 1 : max_watermark_index + 1, 1:
    # ] *= fill_probabilities_from_release
    my_operation(
        arr=self.watermarks,
        watermark_index_above_cloud=watermark_index_above_cloud,
        max_watermark_index=max_watermark_index,
        fill_probabilities_from_release=fill_probabilities_from_release,
    )

    # Current numbers of electrons temporarily in traps and now available
    n_trapped_electrons_tmp = numba_n_trapped_electrons_from_watermarks(
        watermarks=self.watermarks, n_traps_per_pixel=self.n_traps_per_pixel
    )
    n_free_electrons += n_trapped_electrons_initial - n_trapped_electrons_tmp

    # Re-calculate the fractional volume of the electron cloud
    cloud_fractional_volume = self.fraction_of_traps_exposed_from_n_electrons(
        n_electrons=n_free_electrons, ccd_filling_function=ccd_filling_function
    )
    watermark_index_above_cloud = (
        watermark_index_above_cloud_from_cloud_fractional_volume(
            cloud_fractional_volume=cloud_fractional_volume,
            watermarks=self.watermarks,
            max_watermark_index=max_watermark_index,
        )
    )

    # Update the watermark volumes, duplicated for the initial watermarks
    if cloud_fractional_volume > 0 and not value_in_cumsum(
        cloud_fractional_volume, self.watermarks[:, 0]
    ):
        self.watermarks = numba_update_watermark_volumes_for_cloud_below_highest(
            watermarks=self.watermarks,
            cloud_fractional_volume=cloud_fractional_volume,
            watermark_index_above_cloud=watermark_index_above_cloud,
        )
        watermarks_initial = numba_update_watermark_volumes_for_cloud_below_highest(
            watermarks=watermarks_initial,
            cloud_fractional_volume=cloud_fractional_volume,
            watermark_index_above_cloud=watermark_index_above_cloud,
        )

        # Increment the index now that an extra watermark has been set
        max_watermark_index += 1

    return (
        n_free_electrons,
        watermarks_initial,
        cloud_fractional_volume,
        watermark_index_above_cloud,
        max_watermark_index,
    )


#
# def roll_2d_vertical_1( arr):
#     """ Equivalent to np.roll(arr, 1, axis=0) """
#
#     # Unfortunately we cannot use np.zeros without the gil, so good old
#     # fashioned C is used instead
#     cdef np.float64_t * arr_last_row = <np.float64_t *> malloc(
#         sizeof(np.float64_t) * arr.shape[1]
#     )
#     cdef np.int64_t i, j
#
#     # Copy the last row
#     for j in range(0, arr.shape[1], 1):
#         arr_last_row[j] = arr[arr.shape[0] - 1, j]
#
#     # Move all the rows up an index
#     for i in range(1, arr.shape[0], 1):
#         for j in range(0, arr.shape[1], 1):
#             arr[arr.shape[0] - i, j] = arr[arr.shape[0] - i - 1, j]
#
#     # Put the copied last row into the 0 index
#     for j in range(0, arr.shape[1], 1):
#         arr[0, j] = arr_last_row[j]
#
#     free(arr_last_row)


# From 'cy_update_watermark_volumes_for_cloud_below_highest'
# in 'arcticpy/trap_managers_utils.pyx'
@njit
def numba_update_watermark_volumes_for_cloud_below_highest(
    watermarks,
    cloud_fractional_volume,
    watermark_index_above_cloud,
):
    """See update_watermark_volumes_for_cloud_below_highest()"""

    # The volume and cumulative volume of the watermark around the cloud volume
    watermark_fractional_volume = watermarks[watermark_index_above_cloud, 0]
    cumulative_watermark_fractional_volume = 0.0
    old_fractional_volume = 0.0

    for i in range(0, watermark_index_above_cloud + 1, 1):
        cumulative_watermark_fractional_volume += watermarks[i, 0]

    # Move one new empty watermark to the start of the list
    # roll_2d_vertical_1(watermarks)
    _, watermarks_num_x = watermarks.shape
    watermarks = np.roll(watermarks, 1 * watermarks_num_x)

    # Re-set the relevant watermarks near the start of the list
    watermarks_shape_x = watermarks.shape[1]

    if watermark_index_above_cloud == 0:
        for j in range(0, watermarks_shape_x, 1):
            watermarks[0, j] = watermarks[1, j]
    else:
        for i in range(0, watermark_index_above_cloud + 1, 1):
            for j in range(0, watermarks_shape_x, 1):
                watermarks[i, j] = watermarks[i + 1, j]

    # Update the new split watermarks' volumes
    old_fractional_volume = watermark_fractional_volume
    watermarks[watermark_index_above_cloud, 0] = cloud_fractional_volume - (
        cumulative_watermark_fractional_volume - watermark_fractional_volume
    )
    watermarks[watermark_index_above_cloud + 1, 0] = (
        old_fractional_volume - watermarks[watermark_index_above_cloud, 0]
    )
    return watermarks


# From 'TrapManager.update_watermark_volumes_for_cloud_below_highest'
# in 'arcticpy/trap_manager.py'
# self => TrapManager object
def update_watermark_volumes_for_cloud_below_highest(
    # self,
    watermarks,
    cloud_fractional_volume,
    watermark_index_above_cloud,
):

    numba_update_watermark_volumes_for_cloud_below_highest(
        watermarks, cloud_fractional_volume, watermark_index_above_cloud
    )
    return watermarks


# From 'cy_n_trapped_electrons_from_watermarks'
# in 'arcticpy/trap_managers_utils.pyx'
@njit
def numba_n_trapped_electrons_from_watermarks(watermarks, n_traps_per_pixel):
    total = 0.0

    num_y, num_x = watermarks.shape

    for i in range(0, num_y, 1):
        for j in range(1, num_x, 1):
            total += watermarks[i, 0] * watermarks[i, j] * n_traps_per_pixel[j - 1]

    return total


# self => TrapManager object
# def n_trapped_electrons_from_watermarks(
#     # self,
#     n_traps_per_pixel,  # from 'self'
#     watermarks,
# ):
#     return numba_n_trapped_electrons_from_watermarks(watermarks, n_traps_per_pixel)


@njit
def my_func2(watermarks):
    # max_watermark_index = np.argmax(self.watermarks[:, 0] == 0) - 1
    max_watermark_index = np.argmax(watermarks[:, 0] == 0) - 1

    return max_watermark_index


# From 'TrapManager.n_electrons_released_and_captured'
# in 'arcticpy/trap_manager.py'
# self => TrapManager object
def func_n_electrons_released_and_captured(
    self,  # type: TrapManager
    n_free_electrons,
    ccd_filling_function,
    dwell_time=1,
    express_multiplier=1,
):

    # Initial watermarks and number of electrons in traps
    # watermarks_initial = deepcopy(self.watermarks)
    watermarks_initial = np.array(self.watermarks)
    n_trapped_electrons_initial = numba_n_trapped_electrons_from_watermarks(
        watermarks=self.watermarks, n_traps_per_pixel=self.n_traps_per_pixel
    )

    # Probabilities of being full after release and/or capture
    (
        fill_probabilities_from_empty,
        fill_probabilities_from_full,
        fill_probabilities_from_release,
    ) = fill_probabilities_from_dwell_time(
        total_rates=self.total_rates,
        capture_rates=self.capture_rates,
        emission_rates=self.emission_rates,
        dwell_time=dwell_time,
    )

    # Find the highest active watermark
    # max_watermark_index = np.argmax(self.watermarks[:, 0] == 0) - 1
    max_watermark_index = my_func2(watermarks=self.watermarks)

    # The fractional volume the electron cloud reaches in the pixel well
    cloud_fractional_volume = self.fraction_of_traps_exposed_from_n_electrons(
        n_electrons=n_free_electrons, ccd_filling_function=ccd_filling_function
    )

    # Find the first watermark above the cloud
    watermark_index_above_cloud = (
        watermark_index_above_cloud_from_cloud_fractional_volume(
            cloud_fractional_volume=cloud_fractional_volume,
            watermarks=self.watermarks,
            max_watermark_index=max_watermark_index,
        )
    )

    # Proceed with capture depending on the volume of the cloud compared
    # with the existing watermark levels:

    # First capture (no existing watermarks)
    if max_watermark_index == -1 and n_free_electrons > 0:
        # Make the new watermark then can return immediately
        n_trapped_electrons_final = (
            self._n_electrons_released_and_captured__first_capture(
                n_free_electrons,
                cloud_fractional_volume,
                watermarks_initial,
                fill_probabilities_from_empty,
                express_multiplier,
            )
        )

        return n_trapped_electrons_final

    # Cloud fractional volume below existing watermarks (or 0)
    elif (
        watermark_index_above_cloud <= max_watermark_index or max_watermark_index == -1
    ):
        # Create a new watermark at the cloud fractional volume then release
        # electrons from watermarks above the cloud
        (
            n_free_electrons,
            watermarks_initial,
            cloud_fractional_volume,
            watermark_index_above_cloud,
            max_watermark_index,
        ) = _n_electrons_released_and_captured_cloud_below_watermarks(
            self,
            n_free_electrons,
            cloud_fractional_volume,
            watermarks_initial,
            watermark_index_above_cloud,
            max_watermark_index,
            fill_probabilities_from_release,
            n_trapped_electrons_initial,
            ccd_filling_function,
        )
        # Cloud fractional volume above existing watermarks
    else:
        # Initialise the new watermark, duplicated for the initial watermarks
        self.watermarks[
            watermark_index_above_cloud, 0
        ] = cloud_fractional_volume - np.sum(self.watermarks[:, 0])
        watermarks_initial[watermark_index_above_cloud, 0] = self.watermarks[
            watermark_index_above_cloud, 0
        ]

    # Continue with capture having prepared the new watermark at the cloud
    # and released from any watermarks above the cloud

    # Release and capture electrons all the way to watermarks below the cloud
    fill_fractions_old = self.watermarks[: watermark_index_above_cloud + 1, 1:]
    self.watermarks[: watermark_index_above_cloud + 1, 1:] = (
        fill_fractions_old * fill_probabilities_from_full
        + (1 - fill_fractions_old) * fill_probabilities_from_empty
    )

    # Collapse any redundant watermarks that are completely full
    self.watermarks, watermarks_initial = collapse_redundant_watermarks(
        filled_watermark_value=self.filled_watermark_value,
        watermarks=self.watermarks,
        watermarks_copy=watermarks_initial,
    )

    # Final number of electrons in traps
    n_trapped_electrons_final = numba_n_trapped_electrons_from_watermarks(
        watermarks=self.watermarks, n_traps_per_pixel=self.n_traps_per_pixel
    )

    # Prevent division by zero errors
    if n_trapped_electrons_final == n_trapped_electrons_initial:
        return 0

    # Not enough available electrons to capture
    enough = n_free_electrons / (
        n_trapped_electrons_final - n_trapped_electrons_initial
    )
    if 0 < enough < 1:
        # For watermark fill fractions that increased, tweak them such that
        # the resulting increase instead matches the available electrons
        self.watermarks = self.updated_watermarks_from_capture_not_enough(
            watermarks=self.watermarks,
            watermarks_initial=watermarks_initial,
            enough=enough,
        )

        # Final number of electrons in traps
        n_trapped_electrons_final = numba_n_trapped_electrons_from_watermarks(
            watermarks=self.watermarks, n_traps_per_pixel=self.n_traps_per_pixel
        )

    # Collapse any redundant watermarks that are completely full
    self.watermarks = collapse_redundant_watermarks_no_copy(
        filled_watermark_value=self.filled_watermark_value, watermarks=self.watermarks
    )

    return n_trapped_electrons_initial - n_trapped_electrons_final


# From 'cy_clock_charge_in_one_direction'
# in 'arcticpy/main_utils.pyx'
def clock_charge_in_one_direction(
    image_in,
    ccd,
    roe,
    traps,
    express,
    offset,
    window_row_range,
    window_column_range,
    time_window_range,
):

    # Generate the arrays over each step for: the number of of times that the
    # effect of each pixel-to-pixel transfer can be multiplied for the express
    # algorithm; and whether the traps must be monitored (usually whenever
    # express matrix > 0, unless using a time window)
    (
        express_matrix,
        monitor_traps_matrix,
    ) = roe.express_matrix_and_monitor_traps_matrix_from_pixels_and_express(
        pixels=window_row_range,
        express=express,
        offset=offset,
        time_window_range=time_window_range,
    )

    # ; and whether the trap occupancy states must be saved for the next express
    # pass rather than being reset (usually at the end of each express pass)
    save_trap_states_matrix = roe.save_trap_states_matrix_from_express_matrix(
        express_matrix=express_matrix
    )

    # Decide in advance which steps need to be evaluated and which can be skipped
    phases_with_traps = np.array(
        [i for i, frac in enumerate(ccd.fraction_of_traps_per_phase) if frac > 0],
        dtype=np.int64,
    )

    steps_with_nonzero_dwell_time = np.array(
        [i for i, time in enumerate(roe.dwell_times) if time > 0], dtype=np.int64
    )

    # Extract and type lots of things that won't be changed
    n_express_pass = express_matrix.shape[0]
    n_rows_to_process = express_matrix.shape[1]

    # Set up the set of trap managers to monitor the occupancy of all trap species
    if isinstance(roe, ROETrapPumping):
        # For trap pumping there is only one pixel and row to process but
        # multiple transfers back and forth without clearing the watermarks
        # Note, this allows for many more watermarks than are actually needed
        # in standard trap-pumping clock sequences
        max_n_transfers = n_express_pass * steps_with_nonzero_dwell_time.shape[0]
    else:
        max_n_transfers = n_rows_to_process * steps_with_nonzero_dwell_time.shape[0]

    trap_managers = AllTrapManager(
        traps=traps, max_n_transfers=max_n_transfers, ccd=ccd
    )

    # Temporarily expand image, if charge released from traps ever migrates to
    # a different charge packet, at any time during the clocking sequence
    n_rows_zero_padding = max(roe.pixels_accessed_during_clocking) - min(
        roe.pixels_accessed_during_clocking
    )
    zero_padding = np.zeros((n_rows_zero_padding, image_in.shape[1]), dtype=np.float64)

    image = np.concatenate((image_in, zero_padding), axis=0)

    # Read out one column of pixels through the (column of) traps
    for column_index in window_column_range:
        # Monitor the traps in every pixel, or just one (express=1) or a few
        # (express=a few) then replicate their effect
        for express_index in range(n_express_pass):
            # Restore the trap occupancy levels (to empty, or to a saved state
            # from a previous express pass)
            trap_managers.restore()

            # Set the steps that need to be evaluated (may need to monitor the
            # traps and update their occupancies even if express_mulitplier is
            # 0, e.g. for a time window)
            row_indices = np.nonzero(monitor_traps_matrix[express_index])[0]

            # Each pixel
            for i_row in range(row_indices.shape[0]):
                row_index = row_indices[i_row]
                express_multiplier = express_matrix[express_index, row_index]

                for i_clocking_step in range(steps_with_nonzero_dwell_time.shape[0]):
                    clocking_step = steps_with_nonzero_dwell_time[i_clocking_step]

                    for i_phase in range(phases_with_traps.shape[0]):
                        phase = phases_with_traps[i_phase]

                        # Information about the potentials in this phase
                        roe_phase = roe.clock_sequence[clocking_step][phase]

                        # Select the relevant pixel (and phase) for the initial charge
                        row_index_read = (
                            window_row_range[row_index]
                            + roe_phase.capture_from_which_pixel
                        )

                        # Initial charge (0 if this phase's potential is not high)
                        n_free_electrons = (
                            image[row_index_read, column_index] * roe_phase.is_high
                        )

                        # Allow electrons to be released from and captured by traps
                        n_electrons_released_and_captured = 0
                        for trap_manager in trap_managers[phase]:
                            n_electrons_released_and_captured += (
                                func_n_electrons_released_and_captured(
                                    self=trap_manager,
                                    n_free_electrons=n_free_electrons,
                                    dwell_time=roe.dwell_times[clocking_step],
                                    ccd_filling_function=ccd.well_filling_function(
                                        phase=phase
                                    ),
                                    express_multiplier=express_multiplier,
                                )
                            )

                        # Skip updating the image if only monitoring the traps
                        if express_multiplier == 0:
                            continue

                        # Select the relevant pixel (and phase(s)) for the returned charge
                        row_indices_write = (
                            window_row_range[row_index]
                            + roe_phase.release_to_which_pixels
                        )

                        # Return the electrons back to the relevant charge
                        # cloud, or a fraction if they are being returned to
                        # multiple phases
                        for i in range(row_indices_write.shape[0]):
                            row_index_write = row_indices_write[i]
                            image[row_index_write, column_index] += (
                                n_electrons_released_and_captured
                                * roe_phase.release_fraction_to_pixel[i]
                                * express_multiplier
                            )

                            # Make sure image counts don't go negative, as could
                            # otherwise happen with a large express_multiplier
                            if image[row_index_write, column_index] < 0:
                                image[row_index_write, column_index] = 0

                # Save the trap occupancy states for the next express pass
                if save_trap_states_matrix[express_index, row_index]:
                    trap_managers.save()

        # Reset the watermarks for the next column, effectively setting the trap
        # occupancies to zero
        if roe.empty_traps_between_columns:
            trap_managers.empty_all_traps()
        trap_managers.save()

    # Unexpand the image to its original dimensions
    image_out = np.asarray(image)
    if n_rows_zero_padding > 0:
        image_out = image_out[0:-n_rows_zero_padding, :]

    return image_out


# From 'add_cti'
# in 'arcticpy/main.py'
def add_cti(
    image,
    parallel_ccd=None,
    parallel_roe=None,
    parallel_traps=None,
    parallel_express=0,
    parallel_offset=0,
    parallel_window_range=None,
    serial_ccd=None,
    serial_roe=None,
    serial_traps=None,
    serial_express=0,
    serial_offset=0,
    serial_window_range=None,
    time_window_range=None,
):

    n_rows_in_image, n_columns_in_image = image.shape

    # Default windows to the full image; convert single-pixel windows to ranges
    if parallel_window_range is None:
        parallel_window_range = range(n_rows_in_image)
    elif isinstance(parallel_window_range, int):
        parallel_window_range = range(parallel_window_range, parallel_window_range + 1)
    if serial_window_range is None:
        serial_window_range = range(n_columns_in_image)
    elif isinstance(serial_window_range, int):
        serial_window_range = range(serial_window_range, serial_window_range + 1)
    if time_window_range is None:
        time_window_range = range(n_rows_in_image + parallel_offset)
        # Set the "columns" window in the rotated image for serial clocking
        serial_window_column_range = parallel_window_range
    else:
        # Intersection of spatial and time windows for serial clocking
        serial_window_column_range = range(
            int(max(parallel_window_range[0], time_window_range[0] - parallel_offset)),
            int(min(parallel_window_range[-1], time_window_range[-1] - parallel_offset))
            + 1,
        )

    # Default ROE: simple, single-phase clocking in imaging mode
    if parallel_roe is None:
        parallel_roe = ROE()
    if serial_roe is None:
        serial_roe = ROE()

    # Don't modify the external array passed to this function
    image_add_cti = deepcopy(image)

    # Parallel clocking
    if parallel_traps is not None:
        image_add_cti = clock_charge_in_one_direction(
            image_in=image_add_cti,
            ccd=parallel_ccd,
            roe=parallel_roe,
            traps=parallel_traps,
            express=parallel_express,
            offset=parallel_offset,
            window_row_range=parallel_window_range,
            window_column_range=serial_window_range,
            time_window_range=time_window_range,
        )

    # Serial clocking
    if serial_traps is not None:
        # Switch axes, so clocking happens in other direction
        image_add_cti = image_add_cti.T.copy()

        # Transfer charge in serial direction
        image_add_cti = clock_charge_in_one_direction(
            image_in=image_add_cti,
            ccd=serial_ccd,
            roe=serial_roe,
            traps=serial_traps,
            express=serial_express,
            offset=serial_offset,
            window_row_range=serial_window_range,
            window_column_range=serial_window_column_range,
            time_window_range=None,
        )

        # Switch axes back
        image_add_cti = image_add_cti.T

    # TODO : Implement as decorator
    if isinstance(image, frames.Frame):
        return image.__class__(
            array=image_add_cti,
            mask=image.mask,
            original_roe_corner=image.original_roe_corner,
            scans=image.scans,
            exposure_info=image.exposure_info,
        )

    return image_add_cti


def arctic_fast(
    detector: CCD,
    well_fill_power: float,
    density: float,
    release_timescale: t.Sequence[float],
    express=0,
) -> np.ndarray:
    char = detector.characteristics
    image = detector.pixel.array
    image = image.astype(float)
    ccd = ac.CCD(well_fill_power=well_fill_power, full_well_depth=char.fwc)
    roe = ac.ROE()
    trap = ac.Trap(density=density, release_timescale=release_timescale)
    s = add_cti(
        image=image,
        parallel_traps=[trap],
        parallel_ccd=ccd,
        parallel_roe=roe,
        parallel_express=express,
    )
    detector.pixel.array = s
    return s
