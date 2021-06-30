#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.


import os
import typing as t
from copy import deepcopy

import numpy as np
from numba import njit

from pyxel.detectors import CCD as PyxelCCD

NUMBA_DISABLE_JIT = bool(int(os.environ.get("NUMBA_DISABLE_JIT", 0)))  # type: bool


@njit
def set_min_max(value: float, min: float, max: float) -> float:
    """Fix a value between a minimum and maximum."""
    if value < min:
        return min
    elif max < value:
        return max
    else:
        return value


@njit
def my_cumsum_axis0(data_2d: np.ndarray) -> np.ndarray:
    other_data = data_2d.copy()

    num_y = data_2d.shape[0]  # type: int

    for idx in range(1, num_y):
        other_data[idx] = other_data[idx] + other_data[idx - 1]

    return other_data


@njit
def my_roll_axis0(a: np.ndarray, shift: int) -> np.ndarray:
    # Equivalent to np.roll(a, shift, axis=0)
    _, num_x = a.shape
    return np.roll(a, shift * num_x)


class CCD:
    def __init__(
        self,
        n_phases,
        fraction_of_traps_per_phase: np.ndarray,  # =None,
        full_well_depth: np.ndarray,  # = 1e4,
        well_notch_depth: np.ndarray,  # float = 0.0,
        well_fill_power: np.ndarray,  # float = 0.58,
        well_bloom_level: np.ndarray,
    ):
        """
        A model describing how electrons fill the volume inside each phase of
        a pixel in a CCD detector.

        By default, each pixel is assumed to have only a single phase. To
        specify a multi-phase device (which will need a corresponding clocking
        sequence to be defined in readout electronics) specify the fraction of
        traps as a list, and optionally different values for the other
        parameters as lists too. If the trap density is uniform, then the ratio
        of full_well_depth to fraction_of_traps_per_phase will be the same in
        all phases.

        All the following are equivalent:
            ccd.cloud_fractional_volume_from_n_electrons_and_phase(
                n_electrons, phase
            )

            f = ccd.well_filling_function(
                phase
            )
            f(n_electrons)

            p = ac.CCDPhase(ccd, phase)
            p.cloud_fractional_volume_from_n_electrons(n_electrons)


        Parameters
        ----------
        fraction_of_traps_per_phase : float or [float]
            Assuming that traps have uniform density throughout the CCD, for
            multi-phase clocking, this specifies the physical width of each
            phase. This is used only to distribute the traps between phases.
            The units do not matter and can be anything from microns to light
            years, or fractions of a pixel. Only the fractional widths are ever
            returned. If this is an array then you can optionally also enter
            lists of any/all of the other parameters for each phase.

        full_well_depth : float or [float]
            The maximum number of electrons that can be contained within a
            pixel/phase. For multiphase clocking, if only one value is supplied,
            that is (by default) replicated to all phases. However, different
            physical widths of phases can be set by specifying the full well
            depth as a list containing different values. If the potential in
            more than one phase is held high during any stage in the clocking
            cycle, their full well depths are added together. This value is
            indpependent of the fraction of traps allocated to each phase.

        well_notch_depth : float or [float]
            The number of electrons that fit inside a 'notch' at the bottom of a
            potential well, occupying negligible volume and therefore being
            immune to trapping. These electrons still count towards the full
            well depth. The notch depth can, in  principle, vary between phases.

        well_fill_power : float or [float]
            The exponent in a power-law model of the volume occupied by a cloud
            of electrons. This can, in principle, vary between phases.

        well_bloom_level : float or [float]
            Acts similarly to a notch, but for surface traps.
            Default value is full_well_depth - i.e. no blooming is possible.
        """
        assert n_phases > 0
        assert fraction_of_traps_per_phase.shape == (n_phases,)
        assert full_well_depth.shape == (n_phases,)
        assert well_fill_power.shape == (n_phases,)
        assert well_notch_depth.shape == (n_phases,)
        assert well_bloom_level.shape == (n_phases,)

        self.n_phases = n_phases

        # All parameters are returned as a list of length n_phases
        self.fraction_of_traps_per_phase = (
            fraction_of_traps_per_phase
        )  # type: np.ndarray
        self.full_well_depth = full_well_depth  # type: np.ndarray
        self.well_fill_power = well_fill_power  # type: np.ndarray
        self.well_notch_depth = well_notch_depth  # type: np.ndarray
        self.well_bloom_level = well_bloom_level  # type: np.ndarray

    # def well_filling_function(self, phase:int=0) -> t.Callable[[float], float]:
    #     """Return a self-contained function describing the well-filling model.
    #
    #     The returned function calculates the fractional volume of charge cloud
    #     in a pixel (and phase) from the number of electrons in the cloud, which
    #     is used to calculate the proportion of traps that are reached by the
    #     cloud and can capture charge from it.
    #
    #     By default, it is assumed that the traps are uniformly distributed
    #     throughout the volume, but that assumption can be relaxed by adjusting
    #     this function to reflect the net number of traps seen as a function of
    #     charge cloud size. An example would be for surface traps, which are
    #     responsible for blooming (which is asymmetric and happens during
    #     readout, unlike bleeding) and are preset only at the top of a pixel.
    #
    #     This function embodies the core assumption of a volume-driven CTI
    #     model like ArCTIC: that traps are either exposed (and have a
    #     constant capture timescale, which may be zero for instant capture),
    #     or unexposed and therefore unavailable. This behaviour differs from
    #     a density-driven CTI model, in which traps may capture an electron
    #     anywhere in a pixel, but at varying capture probability. There is
    #     considerable evidence that CCDs in the Hubble Space Telescope are
    #     primarily volume-driven; a software algorithm to mimic such behaviour
    #     also runs much faster.
    #
    #     Parameters
    #     ----------
    #     phase : int
    #         The phase of the pixel. Multiple phases may optionally have
    #         different CCD parameters.
    #
    #     Returns
    #     -------
    #     well_filling_function : func
    #         A self-contained function describing the well-filling model for this
    #         phase.
    #     """
    #
    #     def cloud_fractional_volume_from_n_electrons(n_electrons: float, surface:bool=False)->float:
    #         """Calculate the fractional volume of charge cloud.
    #
    #         Parameters
    #         ----------
    #         n_electrons : float
    #             The number of electrons in a charge cloud.
    #
    #         surface : bool
    #             #
    #             # RJM: RESERVED FOR SURFACE TRAPS
    #             #
    #
    #         Returns
    #         -------
    #         volume : float
    #             The fraction of traps of this species exposed.
    #         """
    #         if n_electrons == 0:
    #             return 0
    #
    #         assert surface is False
    #         # if surface:
    #         #     empty = self.blooming_level[phase]
    #         #     beta = 1
    #         #
    #         # else:
    #         #     empty = self.well_notch_depth[phase]  # type: float
    #         #     beta = self.well_fill_power[phase]  # type: float
    #         empty = self.well_notch_depth[phase]  # type: float
    #         beta = self.well_fill_power[phase]  # type: float
    #
    #         well_range = self.full_well_depth[phase] - empty  # type: float
    #
    #         volume = (
    #             set_min_max(value=(n_electrons - empty) / well_range, min=0.0, max=1.0)
    #         ) ** beta
    #
    #         return volume
    #
    #     return cloud_fractional_volume_from_n_electrons

    def my_well_filling_function(self, phase: int, n_electrons: float) -> float:
        """Calculate the fractional volume of charge cloud.

        Parameters
        ----------
        n_electrons : float
            The number of electrons in a charge cloud.

        surface : bool
            #
            # RJM: RESERVED FOR SURFACE TRAPS
            #

        Returns
        -------
        volume : float
            The fraction of traps of this species exposed.
        """
        if n_electrons == 0:
            return 0

        # assert surface is False
        # if surface:
        #     empty = self.blooming_level[phase]
        #     beta = 1
        #
        # else:
        #     empty = self.well_notch_depth[phase]  # type: float
        #     beta = self.well_fill_power[phase]  # type: float
        empty = self.well_notch_depth[phase]  # type: float
        beta = self.well_fill_power[phase]  # type: float

        well_range = self.full_well_depth[phase] - empty  # type: float

        volume = (
            set_min_max(value=(n_electrons - empty) / well_range, min=0.0, max=1.0)
        ) ** beta

        return volume


class ROEPhase:
    def __init__(
        self,
        is_high: bool,
        capture_from_which_pixels: np.ndarray,
        release_to_which_pixels: np.ndarray,
        release_fraction_to_pixel: np.ndarray,
    ):
        """
        Stored information about the electrostatic potentials in a specific phase.

        Parameters
        ----------
        is_high : bool
            Is the potential held high, i.e. able to contain free electrons?

        capture_from_which_pixels : [int]
            The relative row number(s) of the charge cloud to capture from.

        release_to_which_pixels : [int]
            The relative row number(s) of the charge cloud to release to.

        release_fraction_to_pixel : float
            The fraction of the electrons to be released into this pixel.
        """
        assert capture_from_which_pixels.ndim == 1
        assert release_to_which_pixels.ndim == 1
        assert release_fraction_to_pixel.ndim == 1

        # Make sure the arrays are arrays
        self.is_high = is_high  # type: bool
        self.capture_from_which_pixels_1d = (
            capture_from_which_pixels
        )  # type: np.ndarray
        self.release_to_which_pixels_1d = release_to_which_pixels  # type: np.ndarray

        # self.capture_from_which_pixels = np.array(
        #     [capture_from_which_pixels], dtype=np.int64
        # ).flatten()
        # self.release_to_which_pixels = np.array(
        #     [release_to_which_pixels], dtype=np.int64
        # ).flatten()
        self.release_fraction_to_pixel_1d = (
            release_fraction_to_pixel
        )  # type: np.ndarray


# class ROEAbstract:
#     def __init__(
#         self,
#         dwell_times: np.ndarray,
#         # express_matrix_dtype
#     ):
#         """
#         Bare core methods that are shared by all types of ROE.
#
#         Parameters
#         ----------
#         dwell_times : float or [float]
#             The time between steps in the clocking sequence, in the same units
#             as the trap capture/release timescales. This can be a single float
#             for single-step clocking, or a list for multi-step clocking; the
#             number of steps in the clocking sequence is inferred from the length
#             of this list. The default value, [1], produces instantaneous
#             transfer between adjacent pixels, with no intermediate phases.
#
#         express_matrix_dtype : type (int or float)
#             Old versions of this algorithm assumed (unnecessarily) that all
#             express multipliers must be integers. If
#             force_release_away_from_readout is True (no effect if False), then
#             it's slightly more efficient if this requirement is dropped, but the
#             option to force it is included for backwards compatability.
#         """
#         # Parse inputs
#         self.force_release_away_from_readout = None
#         self.dwell_times = dwell_times  # type: np.ndarray
#         # self.express_matrix_dtype = express_matrix_dtype


class ROE:
    def __init__(
        self,
        dwell_times: np.ndarray,  # =[1],
        empty_traps_for_first_transfers: bool = True,
        empty_traps_between_columns: bool = True,
        force_release_away_from_readout: bool = True,
        # express_matrix_dtype=float,
    ):
        """
        The primary readout electronics (ROE) class.

        Parameters
        ----------
        dwell_times : float or [float]
            The time between steps in the clocking sequence, in the same units
            as the trap capture/release timescales. This can be a single float
            for single-step clocking, or a list for multi-step clocking; the
            number of steps in the clocking sequence is inferred from the length
            of this list. The default value, [1], produces instantaneous
            transfer between adjacent pixels, with no intermediate phases.

        empty_traps_for_first_transfers : bool
            If True and if using express != n_pixels, then tweak the express
            algorithm to treat every first pixel-to-pixel transfer separately
            to the rest.

            Physically, the first ixel that a charge cloud finds itself in will
            start with empty traps; whereas every subsequent transfer sees traps
            that may have been filled previously. With the default express
            algorithm, this means the inherently different first-transfer would
            be replicated many times for some pixels but not others. This
            modification prevents that issue by modelling the first single
            transfer for each pixel separately and then using the express
            algorithm normally for the remainder.

        empty_traps_between_columns : bool
            True:  each column has independent traps (appropriate for parallel
                   clocking)
            False: each column moves through the same traps, which therefore
                   preserve occupancy, allowing trails to extend onto the next
                   column (appropriate for serial clocking, if all prescan and
                   overscan pixels are included in the image array).

        force_release_away_from_readout : bool
            If True then force electrons to be released in a pixel further from
            the readout.

        express_matrix_dtype : type : int or float
            Old versions of this algorithm assumed (unnecessarily) that all
            express multipliers must be integers. If
            force_release_away_from_readout is True (no effect if False), then
            it's slightly more efficient if this requirement is dropped, but the
            option to force it is included for backwards compatability.

        Attributes
        ----------
        n_steps : int
            The number of steps in the clocking sequence.

        n_phases : int
            The assumed number of phases in the CCD. This is determined from the
            type, and the number of steps in, the clock sequence. For normal
            readout, the number of clocking steps should be the same as the
            number of CCD phases. This need not true in general, so it is
            defined in a function rather than in __init__.

        clock_sequence : [[ROEPhase]]
            An array of, for each step in a clock sequence, for each phase of
            the CCD, an object with information about the potentials.
        """
        # self._roe_abstract = ROEAbstract(
        #     dwell_times=dwell_times,
        #     # express_matrix_dtype=express_matrix_dtype
        # )
        # From previous 'ROEAbstract'
        self.dwell_times = dwell_times  # type: np.ndarray

        self.n_steps = len(dwell_times)
        self.n_phases = self.n_steps

        # Parse inputs
        self.empty_traps_for_first_transfers = (
            empty_traps_for_first_transfers
        )  # type: bool
        self.empty_traps_between_columns = empty_traps_between_columns  # type: bool
        self.force_release_away_from_readout = (
            force_release_away_from_readout
        )  # type: bool

        # Link to generic methods
        self.clock_sequence = (
            self._generate_clock_sequence()
        )  # type: t.Sequence[t.Sequence[ROEPhase]]
        self.pixels_accessed_during_clocking_1d = (
            self._generate_pixels_accessed_during_clocking()
        )  # type: np.ndarray

    def restrict_time_span_of_express_matrix(
        self, express_matrix_2d: np.ndarray, time_window_range: t.Tuple[int, int]
    ) -> np.ndarray:
        """
        Remove rows of an express_multiplier matrix that are outside a temporal
        region of interest if express were zero.

        Could just remove all other rows; this method is more general.

        Parameters
        ----------
        express_matrix_2d : [[float]]
            The express multiplier value for each pixel-to-pixel transfer.

        time_window_range : range
            The subset of transfers to implement.
        """

        if time_window_range is not None:
            # Work out which pixel-to-pixel transfers a temporal window corresponds to
            time_window_range_start, time_window_range_stop = time_window_range
            window_express_span = time_window_range_stop - time_window_range_start + 1

            # Set to zero entries in all other rows
            # express_matrix = np.cumsum(express_matrix, axis=0) - time_window_range_start
            express_matrix_2d = (
                my_cumsum_axis0(express_matrix_2d) - time_window_range_start
            )

            # express_matrix_2d[express_matrix_2d < 0] = 0
            # express_matrix_2d[
            #     express_matrix_2d > window_express_span
            # ] = window_express_span
            express_matrix_2d = np.where(express_matrix_2d < 0, 0, express_matrix_2d)
            express_matrix_2d = np.where(
                express_matrix_2d > window_express_span,
                window_express_span,
                express_matrix_2d,
            )

            # Undo the cumulative sum
            express_matrix_2d[1:] -= express_matrix_2d[:-1].copy()

        return express_matrix_2d

    def save_trap_states_matrix_from_express_matrix(
        self, express_matrix_2d: np.ndarray
    ) -> np.ndarray:
        """
        Return the accompanying array to the express matrix of when to save
        trap occupancy states.

        Allows the next express iteration can continue from an (approximately)
        suitable configuration.

        If the traps are empty (rather than restored), the first capture in each
        express loop is different from the rest: many electrons are lost. This
        behaviour may be appropriate for the first pixel-to-pixel transfer of
        each charge cloud, but is not for subsequent transfers. It particularly
        causes problems if the first transfer is used to represent many
        transfers, through the express mechanism, as the large loss of electrons
        is multiplied up, replicated throughout many.

        Parameters
        ----------
        express_matrix_2d : [[float]]
            The express multiplier value for each pixel-to-pixel transfer.

        Returns
        -------
        save_trap_states_matrix : [[bool]]
            For each pixel-to-pixel transfer, set True to store the trap
            occupancy levels, so the next express iteration can continue from an
            (approximately) suitable configuration.
        """
        (n_express, n_pixels) = express_matrix_2d.shape
        save_trap_states_matrix_2d = np.zeros((n_express, n_pixels), dtype=np.bool_)

        if not self.empty_traps_for_first_transfers:
            for express_index in range(n_express - 1):
                for row_index in range(n_pixels - 1):
                    if express_matrix_2d[express_index + 1, row_index + 1] > 0:
                        break

                save_trap_states_matrix_2d[express_index, row_index] = True

        return save_trap_states_matrix_2d

    def express_matrix_and_monitor_traps_matrix_from_pixels_and_express(
        self,
        pixels: t.Tuple[int, int],
        express: int,  # =0,
        offset: int,  # =0,
        time_window_range: t.Tuple[int, int],
    ) -> t.Tuple[np.ndarray, np.ndarray]:
        """Calculate the matrices of express multipliers and when to monitor traps.

        To reduce runtime, instead of calculating the effects of every
        pixel-to-pixel transfer, it is possible to approximate readout by
        processing each transfer once (Anderson et al. 2010) or a few times
        (Massey et al. 2014, section 2.1.5), then multiplying the effect of
        that transfer by the number of transfers it represents. This function
        computes the multiplicative factor, and returns it in a matrix that can
        be easily looped over.

        Parameters
        ----------
        pixels : int or range
            The number of pixels in the image, or the subset of pixels to model.

        express : int
            The number of times the pixel-to-pixel transfers are computed,
            determining the balance between accuracy (high values) and speed
            (low values).
                n_pix   (slower, accurate) Compute every pixel-to-pixel
                        transfer. The default 0 = alias for n_pix.
                k       Recompute on k occasions the effect of each transfer.
                        After a few transfers (and e.g. eroded leading edges),
                        the incremental effect of subsequent transfers can
                        change.
                1       (faster, approximate) Compute the effect of each
                        transfer only once.
            Runtime scales approximately as O(express^0.5). ###WIP

        offset : int (>= 0)
            Consider all pixels to be offset by this number of pixels from the
            readout register. Useful if working out the matrix for a postage
            stamp image, or to account for prescan pixels whose data is not
            stored.

        time_window_range : range
            The subset of transfers to implement.

        Returns
        -------
        express_matrix : [[float]]
            The express multiplier value for each pixel-to-pixel transfer.

        monitor_traps_matrix : [[bool]]
            For each pixel-to-pixel transfer, set True if the release and
            capture of charge needs to be monitored.
        """

        # if isinstance(pixels, int):
        #     window_range = range(pixels)
        # else:
        #     window_range = pixels
        window_range_start, window_range_stop = pixels

        # n_pixels = max(window_range) + 1
        n_pixels = window_range_stop - window_range_start + 1  # type: int

        # Set default express to all transfers and check no larger
        if express == 0:
            express = n_pixels + offset
        else:
            express = min((express, n_pixels + offset))

        # Temporarily ignore the first pixel-to-pixel transfer, if it is to be
        # handled differently than the rest
        if self.empty_traps_for_first_transfers and express < n_pixels:
            n_pixels -= 1

        # Initialise an array with enough pixels to contain the supposed image,
        # including offset
        express_matrix_2d = np.empty(
            (express, n_pixels + offset),
            # dtype=self.express_matrix_dtype
            dtype=np.float64,
        )  # type: np.ndarray

        # Compute the multiplier factors
        max_multiplier = (n_pixels + offset) / express  # type: float
        # if self.express_matrix_dtype == int:
        #     max_multiplier = int(np.ceil(max_multiplier))

        # Populate every row in the matrix with a range from 1 to n_pixels +
        # offset (plus 1 because it starts at 1 not 0)
        express_matrix_2d[:] = np.arange(1, n_pixels + offset + 1)

        # Offset each row to account for the pixels that have already been read out
        for express_index in range(express):
            express_matrix_2d[express_index] -= express_index * max_multiplier

        # Truncate all values to between 0 and max_multiplier
        # express_matrix_2d[express_matrix_2d < 0] = 0
        # express_matrix_2d[express_matrix_2d > max_multiplier] = max_multiplier
        express_matrix_2d = np.where(express_matrix_2d < 0, 0, express_matrix_2d)
        express_matrix_2d = np.where(
            express_matrix_2d > max_multiplier, max_multiplier, 0
        )

        # Add an extra (first) transfer for every pixel, the effect of which
        # will only ever be counted once, because it is physically different
        # from the other transfers (it sees only empty traps)
        if self.empty_traps_for_first_transfers and express < n_pixels:
            # Store current matrix, which is correct for one-too-few pixel-to-pixel transfers
            express_matrix_small_2d = express_matrix_2d  # type: np.ndarray
            # Create a new matrix for the full number of transfers
            n_pixels += 1
            express_matrix_2d = np.flipud(
                np.identity(
                    n_pixels + offset,
                    # dtype=self.express_matrix_dtype,
                )
            )
            # Insert the original transfers into the new matrix at appropriate places
            n_nonzero_1d = np.sum(express_matrix_small_2d > 0, axis=1)
            express_matrix_2d[n_nonzero_1d, 1:] += express_matrix_small_2d

        # When to monitor traps
        monitor_traps_matrix_2d = express_matrix_2d > 0
        monitor_traps_matrix_2d = monitor_traps_matrix_2d[:, offset:]
        monitor_traps_matrix_2d = monitor_traps_matrix_2d[
            :, window_range_start:window_range_stop
        ]

        # Extract the desired section of the array
        # Keep only the temporal region of interest (do this last because a: it
        # is faster if operating on a smaller array, and b: it includes the
        # removal of lines that are all zero, some of which might already exist)
        express_matrix_2d = self.restrict_time_span_of_express_matrix(
            express_matrix_2d=express_matrix_2d, time_window_range=time_window_range
        )
        # Remove the offset (which is not represented in the image pixels)
        express_matrix_2d = express_matrix_2d[:, offset:]

        # Keep only the spatial region of interest
        express_matrix_2d = express_matrix_2d[:, window_range_start:window_range_stop]

        return express_matrix_2d, monitor_traps_matrix_2d

    def _generate_clock_sequence(self) -> t.Sequence[t.Sequence[ROEPhase]]:
        """
        The state of the readout electronics at each step of a clocking sequence
        for basic CCD readout with the potential in a single phase held high.

        This function assumes a particular type of sequence that gives sensible
        behaviours set by the user with only self.n_steps and self.n_phases.
        Some variables are set up to be able to account for different and/or
        more complicated sequences in the future, but this is essentially a
        work in progress to become readily customisable by the user.

        Current intended options are primarily:
        self.n_steps = self.n_phases = 1 (default)
        self.n_steps = self.n_phases = 3 (Hubble style)
        self.n_steps = self.n_phases = 4 (Euclid style)
        And works automatically for trap pumping too, by always making the full
        reverse sequence and just ignoring it in normal non-trap-pumping mode.

        Returns
        -------
        clock_sequence : [[ROEPhase]]
            An array of, for each step in a clock sequence, for each phase of
            the CCD, an object with information about the potentials.

        Assumptions:
         * Instant transfer between phases; no traps en route.
         * Electrons released from traps in 'low' phases may be recaptured into
           the same traps or at the bottom of the (nonexistent) potential well,
           depending on the trap_manager functions.
         * At the end of the step, electrons released from traps in 'low' phases
           are moved instantly to the charge cloud in the nearest 'high' phase.
           The electrons are exposed to no traps en route (which is reasonable
           if their capture timescale is nonzero).
         * Electrons that move in this way to trailing charge clouds (higher
           pixel numbers) can/will be captured during step of readout. Electrons
           that move to forward charge clouds would be difficult, and are
           handled by the difference between conceptualisation and
           implementation of the sequence.

        If self.n_steps=1, this generates the most simplistic readout clocking
        sequence, in which every pixel is treated as a single phase, with
        instant transfer of an entire charge cloud to the next pixel.

        For three phases, the diagram below conceptually represents the six
        steps for trap pumping, where charge clouds in high-potential phases
        are shifted first left then back right, or only the first three steps
        for normal readout, where the charge clouds are shifted continuously
        left towards the readout register.

        A trap species in a phase of pixel p could capture electrons when that
        phase's potential is high and a charge cloud is present. The "Capture
        from" lines refer to the original pixel that the cloud was in. So in
        step 3, the charge cloud originally in pixel p+1 has been moved into
        pixel p. For trap pumping, the cloud is then moved back. In normal
        readout it would continue moving towards pixel p-1. The "Release to"
        lines state the pixel to which electrons released by traps in that phase
        will move, essentially into the closest high-potential phase.

        Time          Pixel p-1              Pixel p            Pixel p+1
        Step     Phase2 Phase1 Phase0 Phase2 Phase1 Phase0 Phase2 Phase1 Phase0
        0                     +------+             +------+             +------+
        Capture from          |      |             |   p  |             |      |
        Release to            |      |  p-1     p  |   p  |             |      |
                --------------+      +-------------+      +-------------+      |
        1              +------+             +------+             +------+
        Capture from   |      |             |   p  |             |      |
        Release to     |      |          p  |   p  |   p         |      |
                -------+      +-------------+      +-------------+      +-------
        2       +------+             +------+             +------+
        Capture from   |             |   p  |             |      |
        Release to     |             |   p  |   p     p+1 |      |
                       +-------------+      +-------------+      +--------------
        3                     +------+             +------+             +------+
        Capture from          |      |             |  p+1 |             |      |
        Release to            |      |   p     p+1 |  p+1 |             |      |
                --------------+      +-------------+      +-------------+      |
        4       -------+             +------+             +------+
        Capture from   |             |   p  |             |      |
        Release to     |             |   p  |   p     p+1 |      |
                       +-------------+      +-------------+      +--------------
        5              +------+             +------+             +------+
        Capture from   |      |             |   p  |             |      |
        Release to     |      |          p  |   p  |   p         |      |
                -------+      +-------------+      +-------------+      +-------

        See TestTrapPumping.test__traps_in_different_phases_make_dipoles() in
        test_arcticpy/test_main.py for simple examples using this sequence.

        Note: Doing this with low values of express means that electrons
        released from a 'low' phase and moving forwards (e.g. p-1 above) do not
        necessarily have the chance to be recaptured (depending on the release
        routines in trap_manager, they could be recaptured at the "bottom" of a
        nonexistent potential well, and that is fairly likely because of the
        large volume of their charge cloud). If they do not get captured, and
        tau_c << tau_r (as is usually the case), then this produces a spurious
        leakage of charge from traps. To give them more opportunity to be
        recaptured, we make sure we always end each series of phase-to-phase
        transfers with a high phase that will always allow capture. The release
        operations omitted are irrelevant, because either they were implemented
        during the previous step, or the traps must have been empty anyway.

        If there are an even number of phases, electrons released equidistant
        from two high phases are split in half and sent in both directions. This
        choice means that it should be possible (and fastest) to implement such
        readout using only two phases, with a long dwell time in the phase that
        represents all the 'low' phases.
        """

        n_steps = self.n_steps  # type: int
        n_phases = self.n_phases  # type: int
        integration_step = 0  # type: int

        clock_sequence = []  # type: t.List[t.List[ROEPhase]]
        for step in range(n_steps):
            roe_phases = []  # type: t.List[ROEPhase]

            # Loop counter (0,1,2,3,2,1,... instead of 0,1,2,3,4,5,...) that is
            # relevant during trap pumping and done but ignored in normal modes
            step_prime = integration_step + abs(
                ((step + n_phases) % (n_phases * 2)) - n_phases
            )  # type: int

            # Which phase has its potential held high (able to contain
            # electrons) during this step?
            high_phase = step_prime % n_phases  # type: int

            # Will there be a phase (e.g. half-way between one high phase and
            # the next), from which some released electrons travel in one
            # direction, and others in the opposite direction?
            if (n_phases % 2) == 0:
                split_release_phase = (
                    high_phase + n_phases // 2
                ) % n_phases  # type: int
            else:
                split_release_phase = -1

            for phase in range(n_phases):

                # Where to capture from?
                capture_from_which_pixels = (
                    step_prime - phase + ((n_phases - 1) // 2)
                ) // n_phases  # type: int

                # How many pixels to split the release between?
                n_phases_for_release = 1 + (phase == split_release_phase)  # type: int

                # How much to release into each pixel?
                release_fraction_to_pixel_1d = (
                    np.ones(n_phases_for_release, dtype=np.float64)
                    / n_phases_for_release
                )  # type: np.ndarray

                # Where to release to?
                release_to_which_pixels_1d = capture_from_which_pixels + np.arange(
                    n_phases_for_release, dtype=np.int64
                )  # type: np.ndarray

                # Replace capture/release operations that include a closer-to-
                # readout pixel to instead act on the further-from-readout pixel
                # (i.e. the same operation but on the next pixel in the loop)
                if self.force_release_away_from_readout and phase > high_phase:
                    capture_from_which_pixels += 1
                    release_to_which_pixels_1d += 1

                # Compile results
                roe_phases.append(
                    # Remove keyword arguments because of Numba.
                    ROEPhase(
                        phase == high_phase,
                        np.array([capture_from_which_pixels], dtype=np.int64),
                        release_to_which_pixels_1d,
                        release_fraction_to_pixel_1d,
                    )
                )
            clock_sequence.append(roe_phases)

        return clock_sequence

    def _generate_pixels_accessed_during_clocking(self) -> np.ndarray:
        """
        Return a list of (the relative coordinates to) charge clouds that are
        accessed during the clocking sequence, i.e. p-1, p or p+1 in the diagram
        above.
        """
        referred_to_pixels_1d = np.array([0], dtype=np.int64)
        for step in range(self.n_steps):
            for phase in range(self.n_phases):
                referred_to_pixels_1d = np.concatenate(
                    (
                        referred_to_pixels_1d,
                        self.clock_sequence[step][phase].capture_from_which_pixels_1d,
                        self.clock_sequence[step][phase].release_to_which_pixels_1d,
                    )
                )

        return np.unique(referred_to_pixels_1d)


#
# class Trap:
#     def __init__(
#         self,
#         density:float=0.13,
#         release_timescale:float=0.25,
#         capture_timescale:float=0,
#         surface:bool=False,
#     ):
#         """The parameters for a single trap species.
#
#         Controls the density of traps and the timescales/probabilities of
#         capture and release, along with utilities for the watermarking tracking
#         of trap states and the calculation of capture and release.
#
#         Parameters
#         ----------
#         density : float
#             The density of the trap species in a pixel.
#
#         release_timescale : float
#             The release timescale of the trap, in the same units as the time
#             spent in each pixel or phase (Clocker sequence).
#
#         capture_timescale : float
#             The capture timescale of the trap. Default 0 for instant capture.
#
#         surface : bool
#             #
#             # RJM: RESERVED FOR SURFACE TRAPS
#             #
#
#         Attributes
#         ----------
#         capture_rate, emission_rate : float
#             The capture and emission rates (Lindegren (1998) section 3.2).
#         """
#
#         self.density = float(density)
#         self.release_timescale = release_timescale  # type: float
#         self.capture_timescale = capture_timescale  # type: float
#         self.surface = surface  # type: bool
#
#         # Rates
#         self.emission_rate = 1 / self.release_timescale  # type: float
#
#         if self.capture_timescale == 0:
#             self.capture_rate = np.inf  # type: float
#         else:
#             self.capture_rate = 1 / self.capture_timescale

# def distribution_within_pixel(self, fractional_volume=0):
#     if self.surface:
#         #
#         # RJM: RESERVED FOR SURFACE TRAPS OR SPECIES WITH NONUNIFORM DENSITY WITHIN A PIXEL
#         #
#         pass
#     return None

# TODO: This is new
class Traps:
    def __init__(
        self,
        density_1d: np.ndarray,
        release_timescale_1d: np.ndarray,
        capture_timescale_1d: np.ndarray,
        surface_1d: np.ndarray,
    ):
        assert density_1d.ndim == 1
        assert (
            density_1d.shape
            == release_timescale_1d.shape
            == capture_timescale_1d.shape
            == surface_1d.shape
        )

        self.n_trap_species = len(density_1d)

        self.density_1d = density_1d  # type: np.ndarray
        self.release_timescale_1d = release_timescale_1d  # type: np.ndarray
        self.capture_timescale_1d = capture_timescale_1d  # type: np.ndarray
        self.surface_1d = surface_1d  # type: np.ndarray

        # Rates
        self.emission_rate_1d = 1.0 / self.release_timescale_1d  # type: np.ndarray
        self.capture_rate_1d = 1.0 / self.capture_timescale_1d  # type: np.ndarray


class TrapManager:
    def __init__(self, traps: Traps, max_n_transfers: int):
        """
        The manager for potentially multiple trap species that are able to use
        watermarks in the same way as each other.

        Parameters
        ----------
        traps : Trap or [Trap]
            A list of one or more trap species. Species listed together must be
            able to share watermarks - i.e. they must be similarly distributed
            throughout the pixel volume, and all their states must be stored
            either by occupancy or by time since filling.
            e.g. [bulk_trap_slow,bulk_trap_fast]

        max_n_transfers : int
            The number of pixels containing traps that charge will be expected
            to move. This determines the maximum number of possible capture/
            release events that could create new watermark levels, and is used
            to initialise the watermark array to be only as large as needed, for
            efficiency.

        Attributes
        ----------
        watermarks : np.ndarray
            Array of watermark fractional volumes and fill fractions to describe
            the trap states. Lists each (active) watermark fractional volume and
            the corresponding fill fractions of each trap species. Inactive
            elements are set to 0.

            [[volume, fill, fill, ...],
             [volume, fill, fill, ...],
             ...                       ]

        n_traps_per_pixel : np.ndarray
            The densities of all the trap species.

        capture_rates, emission_rates, total_rates : np.ndarray
            The rates of capture, emission, and their sum for all the traps.

        """
        # if not isinstance(traps, list):
        #     traps = [traps]

        self._n_trap_species = traps.n_trap_species  # type: int
        # self.traps = traps.copy()  # type: Traps
        self.max_n_transfers = max_n_transfers  # type: int

        # Set up the watermark array
        self.watermarks_2d = np.zeros(
            (
                # This +1 is to ensure there is always at least one zero, even
                # if all transfers create a new watermark. The zero is used to
                # find the highest used watermark
                1 + self.max_n_transfers * self.n_watermarks_per_transfer,
                # This +1 is to make space for the volume column
                1 + self.n_trap_species,
            ),
            dtype=np.float64,
        )  # type: np.ndarray

        # Trap rates
        # self.capture_rates_1d = np.array([trap.capture_rate for trap in traps])
        # self.emission_rates_1d = np.array([trap.emission_rate for trap in traps])
        self.capture_rates_1d = traps.capture_rate_1d.copy()  # type: np.ndarray
        self.emission_rates_1d = traps.emission_rate_1d.copy()  # type: np.ndarray
        self.total_rates_1d = self.capture_rates_1d + self.emission_rates_1d

        # Are they surface traps?
        # self.surface_1d = np.array([trap.surface_1d for trap in traps], dtype=np.bool_)
        self.surface_1d = traps.surface_1d.copy()  # type: np.ndarray

        # self.trap_densities_1d = np.array(
        #     [trap.density for trap in self.traps], dtype=np.float64
        # )
        self.trap_densities_1d = traps.density_1d.copy()  # type: np.ndarray

        # Construct a function that describes the fraction of traps that are
        # exposed by a charge cloud containing n_electrons. This must be
        # fractional (rather than the absolute number of traps) because it can
        # be shared between trap species that have different trap densities.
        # if self.traps[0].distribution_within_pixel() == None:
        #
        #     def _fraction_of_traps_exposed_from_n_electrons(
        #         self, n_electrons, ccd_filling_function, surface=self.surface[0]
        #     ):
        #         return ccd_filling_function(n_electrons)
        #
        # else:
        #
        #     def _fraction_of_traps_exposed_from_n_electrons(
        #         self, n_electrons, ccd_filling_function
        #     ):
        #         fraction_of_traps = 0
        #         #
        #         # RJM: RESERVED FOR SURFACE TRAPS OR SPECIES WITH NONUNIFORM DENSITY WITHIN A PIXEL
        #         #
        #         return fraction_of_traps
        #
        # self._fraction_of_traps_exposed_from_n_electrons = (
        #     _fraction_of_traps_exposed_from_n_electrons
        # )

    # TODO: New method not yet validated
    def copy(self) -> "TrapManager":
        # Create new traps
        traps_copied = Traps(
            density_1d=self.trap_densities_1d,
            release_timescale_1d=np.zeros_like(
                self.trap_densities_1d, dtype=np.float64
            ),
            capture_timescale_1d=self.capture_rates_1d,
            surface_1d=self.surface_1d,
        )

        trap_manager_copied = TrapManager(
            traps=traps_copied, max_n_transfers=self.max_n_transfers
        )
        trap_manager_copied.watermarks_2d = self.watermarks_2d.copy()

        return trap_manager_copied

    def fraction_of_traps_exposed_from_n_electrons(
        self,
        n_electrons: float,
        # ccd_filling_function: t.Callable
        ccd: CCD,
        phase: int,
    ):
        """Calculate the proportion of traps reached by a charge cloud."""
        # Do not use keyword arguments (because of Numba)
        return ccd.my_well_filling_function(phase, n_electrons)

    @property
    def n_watermarks_per_transfer(self) -> int:
        """Each transfer can create up to 2 new watermark levels (at the other
        extreme, a transfer can remove all watermarks bar one)
        """
        return 2

    @property
    def n_trap_species(self) -> int:
        """Total number of trap species within this trap manager"""
        return self._n_trap_species

    @property
    def n_traps_per_pixel(self) -> np.ndarray:
        """Number of traps of each species, in each pixel"""
        return self.trap_densities_1d

    @n_traps_per_pixel.setter
    def n_traps_per_pixel(self, values_1d: np.ndarray) -> None:
        assert values_1d.shape == self.trap_densities_1d.shape

        self.trap_densities_1d = values_1d

    @property
    def filled_watermark_value(self):
        """The value for a full watermark level, here 1 because we are
        monitoring the fill fraction.
        """
        return 1

    def n_trapped_electrons_from_watermarks(self, watermarks_2d: np.ndarray) -> float:
        """Sum the total number of electrons currently held in traps.

        Parameters
        ----------
        watermarks_2d : np.ndarray
            The watermarks. See
            initial_watermarks_from_n_pixels_and_total_traps().
        """
        return np.sum(
            (watermarks_2d[:, 0] * watermarks_2d[:, 1:].T).T * self.n_traps_per_pixel
        )

    def empty_all_traps(self) -> None:
        """Reset the trap watermarks for the next run of release and capture."""
        self.watermarks_2d.fill(0.0)

    def fill_probabilities_from_dwell_time(
        self, dwell_time: float
    ) -> t.Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """The probabilities of being full after release and/or capture.

        See Lindegren (1998) section 3.2.

        Parameters
        ----------
        dwell_time : float
            The time spent in this pixel or phase, in the same units as the
            trap timescales.

        Returns
        -------
        fill_probabilities_from_empty : float
            The fraction of traps that were empty that become full.

        fill_probabilities_from_full : float
            The fraction of traps that were full that stay full.

        fill_probabilities_from_release : float
            The fraction of traps that were full that stay full after release.
        """
        # Common factor for capture and release probabilities
        exponential_factor = (
            1 - np.exp(-self.total_rates_1d * dwell_time)
        ) / self.total_rates_1d

        # New fill fraction for empty traps (Eqn. 20)
        # Ignore unnecessary warning from instant capture
        # with warnings.catch_warnings():
        #     warnings.filterwarnings(
        #         "ignore", message="invalid value encountered in multiply"
        #     )
        #     fill_probabilities_from_empty_1d = self.capture_rates_1d * exponential_factor
        fill_probabilities_from_empty_1d = self.capture_rates_1d * exponential_factor

        # Fix for instant capture
        fill_probabilities_from_empty_1d[np.isnan(fill_probabilities_from_empty_1d)] = 1

        # New fill fraction for filled traps (Eqn. 21)
        fill_probabilities_from_full_1d = (
            1 - self.emission_rates_1d * exponential_factor
        )

        # New fill fraction from only release
        fill_probabilities_from_release_1d = np.exp(
            -self.emission_rates_1d * dwell_time
        )

        return (
            fill_probabilities_from_empty_1d,
            fill_probabilities_from_full_1d,
            fill_probabilities_from_release_1d,
        )

    def watermark_index_above_cloud_from_cloud_fractional_volume(
        self,
        cloud_fractional_volume: float,
        watermarks_2d: np.ndarray,
        max_watermark_index: int,
    ) -> int:
        """Return the index of the first watermark above the cloud.

        Parameters
        ----------
        cloud_fractional_volume : float
            The fractional volume of the electron cloud in the pixel.

        watermarks_2d : np.ndarray
            The initial watermarks. See
            initial_watermarks_from_n_pixels_and_total_traps().

        max_watermark_index : int
            The index of the highest existing watermark.

        Returns
        -------
        watermark_index_above_cloud : int
            The index of the first watermark above the cloud.
        """
        if np.sum(watermarks_2d[:, 0]) < cloud_fractional_volume:
            return max_watermark_index + 1

        elif cloud_fractional_volume == 0:
            return -1

        else:
            result = np.argmax(
                cloud_fractional_volume <= np.cumsum(watermarks_2d[:, 0])
            )

            return result

    def updated_watermarks_from_capture_not_enough(
        self,
        watermarks_2d: np.ndarray,
        watermarks_initial_2d: np.ndarray,
        enough: float,
    ) -> np.ndarray:
        """
        Tweak trap watermarks for capturing electrons when not enough are
        available to fill every trap below the cloud fractional volume (rare!).

        Parameters
        ----------
        watermarks_2d : np.ndarray
            The current watermarks after attempted capture. See
            initial_watermarks_from_n_pixels_and_total_traps().

        watermarks_initial_2d : np.ndarray
            The initial watermarks before capture, but with updated fractional
            volumes to match the current watermarks.

        enough : float
            The ratio of available electrons to traps up to this fractional
            volume.

        Returns
        -------
        watermarks : np.ndarray
            The updated watermarks. See
            initial_watermarks_from_n_pixels_and_total_traps().
        """

        # Limit the increase to the `enough` fraction of the original
        watermarks_2d[:, 1:] = (
            enough * watermarks_2d[:, 1:] + (1 - enough) * watermarks_initial_2d[:, 1:]
        )

        return watermarks_2d

    def _n_electrons_released_and_captured__first_capture(
        self,
        n_free_electrons: float,
        cloud_fractional_volume: float,
        watermarks_initial_2d: np.ndarray,
        fill_probabilities_from_empty_1d: np.ndarray,
        express_multiplier: float,
    ) -> float:
        """For n_electrons_released_and_captured(), for the first capture.

        Make the new watermark then can return immediately.
        """

        # Update the watermark volume, duplicated for the initial watermarks
        self.watermarks_2d[0, 0] = cloud_fractional_volume
        watermarks_initial_2d[0, 0] = self.watermarks_2d[0, 0]

        # Update the fill fractions
        self.watermarks_2d[0, 1:] = fill_probabilities_from_empty_1d

        # Final number of electrons in traps
        n_trapped_electrons_final = self.n_trapped_electrons_from_watermarks(
            watermarks_2d=self.watermarks_2d
        )  # type: float

        # Not enough available electrons to capture
        if n_trapped_electrons_final == 0.0:
            return 0.0

        enough = n_free_electrons / n_trapped_electrons_final  # type: float
        if enough < 1.0:
            # For watermark fill fractions that increased, tweak them such that
            # the resulting increase instead matches the available electrons
            self.watermarks_2d = self.updated_watermarks_from_capture_not_enough(
                watermarks_2d=self.watermarks_2d,
                watermarks_initial_2d=watermarks_initial_2d,
                enough=enough,
            )

            # Final number of electrons in traps
            n_trapped_electrons_final = self.n_trapped_electrons_from_watermarks(
                watermarks_2d=self.watermarks_2d
            )

        return -n_trapped_electrons_final

    def update_watermark_volumes_for_cloud_below_highest(
        self,
        watermarks_2d: np.ndarray,
        cloud_fractional_volume: float,
        watermark_index_above_cloud: int,
    ) -> np.ndarray:
        """Update the trap watermarks for a cloud below the highest watermark.

        Parameters
        ----------
        watermarks_2d : np.ndarray
            The initial watermarks. See
            initial_watermarks_from_n_pixels_and_total_traps().

        cloud_fractional_volume : float
            The fractional volume of the electron cloud in the pixel.

        watermark_index_above_cloud : int
            The index of the first watermark above the cloud.

        Returns
        -------
        watermarks : np.ndarray
            The updated watermarks. See
            initial_watermarks_from_n_pixels_and_total_traps().
        """
        # The volume and cumulative volume of the watermark around the cloud volume
        watermark_fractional_volume = watermarks_2d[watermark_index_above_cloud, 0]
        cumulative_watermark_fractional_volume = np.sum(
            watermarks_2d[: watermark_index_above_cloud + 1, 0]
        )

        # Move one new empty watermark to the start of the list
        watermarks_2d = my_roll_axis0(watermarks_2d, 1)

        # Re-set the relevant watermarks near the start of the list
        if watermark_index_above_cloud == 0:
            watermarks_2d[0] = watermarks_2d[1]
        else:
            watermarks_2d[: watermark_index_above_cloud + 1] = watermarks_2d[
                1 : watermark_index_above_cloud + 2
            ]

        # Update the new split watermarks' volumes
        old_fractional_volume = watermark_fractional_volume
        watermarks_2d[watermark_index_above_cloud, 0] = cloud_fractional_volume - (
            cumulative_watermark_fractional_volume - watermark_fractional_volume
        )
        watermarks_2d[watermark_index_above_cloud + 1, 0] = (
            old_fractional_volume - watermarks_2d[watermark_index_above_cloud, 0]
        )

        return watermarks_2d

    def _n_electrons_released_and_captured__cloud_below_watermarks(
        self,
        n_free_electrons: float,
        cloud_fractional_volume: float,
        watermarks_initial_2d: np.ndarray,
        watermark_index_above_cloud: int,
        max_watermark_index: int,
        fill_probabilities_from_release_1d: np.ndarray,
        n_trapped_electrons_initial: float,
        # ccd_filling_function: t.Callable,
        ccd: CCD,
        phase: int,
    ) -> t.Tuple[float, np.ndarray, float, int, int]:
        """For n_electrons_released_and_captured(), for capture from a cloud
            below the existing watermarks.

        Create a new watermark at the cloud fractional volume then release
        electrons from watermarks above the cloud.
        """
        # Create the new watermark at the cloud fractional volume
        if cloud_fractional_volume > 0.0 and cloud_fractional_volume not in np.cumsum(
            self.watermarks_2d[:, 0]
        ):
            # Update the watermark volumes, duplicated for the initial watermarks
            self.watermarks_2d = self.update_watermark_volumes_for_cloud_below_highest(
                watermarks_2d=self.watermarks_2d,
                cloud_fractional_volume=cloud_fractional_volume,
                watermark_index_above_cloud=watermark_index_above_cloud,
            )
            watermarks_initial_2d = (
                self.update_watermark_volumes_for_cloud_below_highest(
                    watermarks_2d=watermarks_initial_2d,
                    cloud_fractional_volume=cloud_fractional_volume,
                    watermark_index_above_cloud=watermark_index_above_cloud,
                )
            )

            # Increment the index now that an extra watermark has been set
            max_watermark_index += 1

        # Release electrons from existing watermark levels above the cloud
        # Update the fill fractions
        self.watermarks_2d[
            watermark_index_above_cloud + 1 : max_watermark_index + 1, 1:
        ] *= fill_probabilities_from_release_1d

        # Current numbers of electrons temporarily in traps and now available
        n_trapped_electrons_tmp = self.n_trapped_electrons_from_watermarks(
            watermarks_2d=self.watermarks_2d
        )  # type: float
        n_free_electrons += n_trapped_electrons_initial - n_trapped_electrons_tmp

        # Re-calculate the fractional volume of the electron cloud
        cloud_fractional_volume = self.fraction_of_traps_exposed_from_n_electrons(
            n_electrons=n_free_electrons,
            # ccd_filling_function=ccd_filling_function
            ccd=ccd,
            phase=phase,
        )

        watermark_index_above_cloud = (
            self.watermark_index_above_cloud_from_cloud_fractional_volume(
                cloud_fractional_volume=cloud_fractional_volume,
                watermarks_2d=self.watermarks_2d,
                max_watermark_index=max_watermark_index,
            )
        )

        # Update the watermark volumes, duplicated for the initial watermarks
        if cloud_fractional_volume > 0.0 and cloud_fractional_volume not in np.cumsum(
            self.watermarks_2d[:, 0]
        ):
            self.watermarks_2d = self.update_watermark_volumes_for_cloud_below_highest(
                watermarks_2d=self.watermarks_2d,
                cloud_fractional_volume=cloud_fractional_volume,
                watermark_index_above_cloud=watermark_index_above_cloud,
            )
            watermarks_initial_2d = (
                self.update_watermark_volumes_for_cloud_below_highest(
                    watermarks_2d=watermarks_initial_2d,
                    cloud_fractional_volume=cloud_fractional_volume,
                    watermark_index_above_cloud=watermark_index_above_cloud,
                )
            )

            # Increment the index now that an extra watermark has been set
            max_watermark_index += 1

        return (
            n_free_electrons,
            watermarks_initial_2d,
            cloud_fractional_volume,
            watermark_index_above_cloud,
            max_watermark_index,
        )

    def collapse_redundant_watermarks_with_copy(
        self, watermarks_2d: np.ndarray, watermarks_copy_2d: np.ndarray
    ) -> t.Tuple[np.ndarray, np.ndarray]:
        """
        Collapse any redundant watermarks that are completely full.

        Parameters
        ----------
        watermarks_2d : np.ndarray
            The current watermarks. See
            initial_watermarks_from_n_pixels_and_total_traps().

        watermarks_copy_2d : np.ndarray
            A copy of the watermarks array that should be edited in the same way
            as watermarks.

        Returns
        -------
        watermarks : np.ndarray
            The updated watermarks. See
            initial_watermarks_from_n_pixels_and_total_traps().

        watermarks_copy : np.ndarray
            The updated watermarks copy, if it was provided.
        """

        # Number of trap species
        num_traps = len(watermarks_2d[0, 1:])  # type: int

        # Find the first watermark that is not completely filled for all traps
        watermark_index_not_filled = min(
            [
                np.argmax(watermarks_2d[:, 1 + i_trap] != self.filled_watermark_value)
                for i_trap in range(num_traps)
            ]
        )  # type: int

        # Skip if none or only one are completely filled
        if watermark_index_not_filled <= 1:
            # if watermarks_copy_2d is not None:
            #     return watermarks_2d, watermarks_copy_2d
            # else:
            #     return watermarks_2d
            return watermarks_2d, watermarks_copy_2d

        # Total fractional volume of filled watermarks
        fractional_volume_filled = np.sum(
            watermarks_2d[:watermark_index_not_filled, 0]
        )  # type: float

        # Combined fill values
        # if watermarks_copy_2d is not None:
        #     # Multiple trap species
        #     if 1 < num_traps:
        #         axis = 1
        #     else:
        #         axis = None
        #     copy_fill_values = np.sum(
        #         watermarks_copy_2d[:watermark_index_not_filled, 0]
        #         * watermarks_copy_2d[:watermark_index_not_filled, 1:].T,
        #         axis=axis,
        #     ) / np.sum(watermarks_copy_2d[:watermark_index_not_filled, 0])

        # Multiple trap species
        assert num_traps == 1
        # if 1 < num_traps:
        #     axis = 1
        # else:
        #     axis = None
        # copy_fill_values = np.sum(
        #     watermarks_copy_2d[:watermark_index_not_filled, 0]
        #     * watermarks_copy_2d[:watermark_index_not_filled, 1:].T,
        #     axis=axis,
        # ) / np.sum(
        #     watermarks_copy_2d[:watermark_index_not_filled, 0]
        # )  # type: float
        copy_fill_values = np.sum(
            watermarks_copy_2d[:watermark_index_not_filled, 0]
            * watermarks_copy_2d[:watermark_index_not_filled, 1:].T,
        ) / np.sum(
            watermarks_copy_2d[:watermark_index_not_filled, 0]
        )  # type: float

        # Remove the no-longer-needed overwritten watermarks
        watermarks_2d[:watermark_index_not_filled, :] = 0.0
        # if watermarks_copy_2d is not None:
        #     watermarks_copy_2d[:watermark_index_not_filled, :] = 0
        watermarks_copy_2d[:watermark_index_not_filled, :] = 0.0

        # Move the no-longer-needed watermarks to the end of the list
        watermarks_2d = my_roll_axis0(watermarks_2d, 1 - watermark_index_not_filled)
        # if watermarks_copy_2d is not None:
        #     watermarks_copy_2d = np.roll(
        #         watermarks_copy_2d, 1 - watermark_index_not_filled, axis=0
        #     )
        watermarks_copy_2d = my_roll_axis0(
            watermarks_copy_2d, 1 - watermark_index_not_filled
        )

        # Edit the new first watermark
        watermarks_2d[0, 0] = fractional_volume_filled
        watermarks_2d[0, 1:] = self.filled_watermark_value
        # if watermarks_copy_2d is not None:
        #     watermarks_copy_2d[0, 0] = fractional_volume_filled
        #     watermarks_copy_2d[0, 1:] = copy_fill_values
        watermarks_copy_2d[0, 0] = fractional_volume_filled
        watermarks_copy_2d[0, 1:] = copy_fill_values

        # if watermarks_copy_2d is not None:
        #     return watermarks_2d, watermarks_copy_2d
        # else:
        #     return watermarks_2d
        return watermarks_2d, watermarks_copy_2d

    def collapse_redundant_watermarks_without_copy(
        self, watermarks_2d: np.ndarray
    ) -> np.ndarray:
        """
        Collapse any redundant watermarks that are completely full.

        Parameters
        ----------
        watermarks_2d : np.ndarray
            The current watermarks. See
            initial_watermarks_from_n_pixels_and_total_traps().

        watermarks_copy_2d : np.ndarray
            A copy of the watermarks array that should be edited in the same way
            as watermarks.

        Returns
        -------
        watermarks : np.ndarray
            The updated watermarks. See
            initial_watermarks_from_n_pixels_and_total_traps().

        watermarks_copy : np.ndarray
            The updated watermarks copy, if it was provided.
        """

        # Number of trap species
        num_traps = len(watermarks_2d[0, 1:])  # type: int

        # Find the first watermark that is not completely filled for all traps
        watermark_index_not_filled = min(
            [
                np.argmax(watermarks_2d[:, 1 + i_trap] != self.filled_watermark_value)
                for i_trap in range(num_traps)
            ]
        )  # type: int

        # Skip if none or only one are completely filled
        if watermark_index_not_filled <= 1:
            # if watermarks_copy_2d is not None:
            #     return watermarks_2d, watermarks_copy_2d
            # else:
            #     return watermarks_2d
            return watermarks_2d

        # Total fractional volume of filled watermarks
        fractional_volume_filled = np.sum(
            watermarks_2d[:watermark_index_not_filled, 0]
        )  # type: float

        # Combined fill values
        # if watermarks_copy_2d is not None:
        #     # Multiple trap species
        #     if 1 < num_traps:
        #         axis = 1
        #     else:
        #         axis = None
        #     copy_fill_values = np.sum(
        #         watermarks_copy_2d[:watermark_index_not_filled, 0]
        #         * watermarks_copy_2d[:watermark_index_not_filled, 1:].T,
        #         axis=axis,
        #     ) / np.sum(watermarks_copy_2d[:watermark_index_not_filled, 0])

        # Remove the no-longer-needed overwritten watermarks
        watermarks_2d[:watermark_index_not_filled, :] = 0.0
        # if watermarks_copy_2d is not None:
        #     watermarks_copy_2d[:watermark_index_not_filled, :] = 0

        # Move the no-longer-needed watermarks to the end of the list
        watermarks_2d = my_roll_axis0(watermarks_2d, 1 - watermark_index_not_filled)
        # if watermarks_copy_2d is not None:
        #     watermarks_copy_2d = np.roll(
        #         watermarks_copy_2d, 1 - watermark_index_not_filled, axis=0
        #     )

        # Edit the new first watermark
        watermarks_2d[0, 0] = fractional_volume_filled
        watermarks_2d[0, 1:] = self.filled_watermark_value
        # if watermarks_copy_2d is not None:
        #     watermarks_copy_2d[0, 0] = fractional_volume_filled
        #     watermarks_copy_2d[0, 1:] = copy_fill_values

        # if watermarks_copy_2d is not None:
        #     return watermarks_2d, watermarks_copy_2d
        # else:
        #     return watermarks_2d
        return watermarks_2d

    def n_electrons_released_and_captured(
        self,
        n_free_electrons: float,
        # ccd_filling_function: t.Callable,
        ccd: CCD,
        phase: int,
        dwell_time: float = 1.0,
        express_multiplier: float = 1.0,
    ) -> float:
        """Release and capture electrons and update the trap watermarks.

        See Lindegren (1998) section 3.2.

        Parameters
        ----------
        n_free_electrons : float
            The number of available electrons for trapping.

        ccd_filling_function : func
            A (self-contained) function describing the well-filling model,
            returning the fractional volume of charge cloud in a pixel from
            the number of electrons in the cloud.

        dwell_time : float
            The time spent in this pixel or phase, in the same units as the
            trap timescales.

        express_multiplier : int
            (Not currently used.)

            The number of times this transfer is to be replicated as part of the
            express algorithm, passed here to make sure that too many electrons
            are not removed if the multiplier is too high, to avoid ending up
            with negative charge in the image.

        Returns
        -------
        net_n_electrons_released : float
            The net number of released (if +ve) and captured (if -ve) electrons.

        Updates
        -------
        watermarks : np.ndarray
            The updated watermarks. See
            initial_watermarks_from_n_pixels_and_total_traps().
        """
        # Initial watermarks and number of electrons in traps
        watermarks_initial_2d = self.watermarks_2d.copy()  # type: np.ndarray
        n_trapped_electrons_initial = self.n_trapped_electrons_from_watermarks(
            watermarks_2d=self.watermarks_2d
        )  # type: float

        # Probabilities of being full after release and/or capture
        (
            fill_probabilities_from_empty_1d,
            fill_probabilities_from_full_1d,
            fill_probabilities_from_release_1d,
        ) = self.fill_probabilities_from_dwell_time(dwell_time=dwell_time)

        # Find the highest active watermark
        max_watermark_index = np.argmax(self.watermarks_2d[:, 0] == 0) - 1  # type: int

        # The fractional volume the electron cloud reaches in the pixel well
        cloud_fractional_volume = self.fraction_of_traps_exposed_from_n_electrons(
            n_electrons=n_free_electrons,
            ccd=ccd,
            phase=phase
            # ccd_filling_function=ccd_filling_function,
        )  # type: float

        # Find the first watermark above the cloud
        watermark_index_above_cloud = (
            self.watermark_index_above_cloud_from_cloud_fractional_volume(
                cloud_fractional_volume=cloud_fractional_volume,
                watermarks_2d=self.watermarks_2d,
                max_watermark_index=max_watermark_index,
            )
        )  # type: int

        # Proceed with capture depending on the volume of the cloud compared
        # with the existing watermark levels:

        # First capture (no existing watermarks)
        if max_watermark_index == -1 and n_free_electrons > 0.0:
            # Make the new watermark then can return immediately
            n_trapped_electrons_final = (
                self._n_electrons_released_and_captured__first_capture(
                    n_free_electrons=n_free_electrons,
                    cloud_fractional_volume=cloud_fractional_volume,
                    watermarks_initial_2d=watermarks_initial_2d,
                    fill_probabilities_from_empty_1d=fill_probabilities_from_empty_1d,
                    express_multiplier=express_multiplier,
                )
            )  # type: float

            return n_trapped_electrons_final

        # Cloud fractional volume below existing watermarks (or 0)
        elif (
            watermark_index_above_cloud <= max_watermark_index
            or max_watermark_index == -1
        ):
            # Create a new watermark at the cloud fractional volume then release
            # electrons from watermarks above the cloud
            (
                n_free_electrons,
                watermarks_initial_2d,
                cloud_fractional_volume,
                watermark_index_above_cloud,
                max_watermark_index,
            ) = self._n_electrons_released_and_captured__cloud_below_watermarks(
                n_free_electrons=n_free_electrons,
                cloud_fractional_volume=cloud_fractional_volume,
                watermarks_initial_2d=watermarks_initial_2d,
                watermark_index_above_cloud=watermark_index_above_cloud,
                max_watermark_index=max_watermark_index,
                fill_probabilities_from_release_1d=fill_probabilities_from_release_1d,
                n_trapped_electrons_initial=n_trapped_electrons_initial,
                # ccd_filling_function=ccd_filling_function,
                ccd=ccd,
                phase=phase,
            )

        # Cloud fractional volume above existing watermarks
        else:
            # Initialise the new watermark, duplicated for the initial watermarks
            self.watermarks_2d[
                watermark_index_above_cloud, 0
            ] = cloud_fractional_volume - np.sum(self.watermarks_2d[:, 0])
            watermarks_initial_2d[watermark_index_above_cloud, 0] = self.watermarks_2d[
                watermark_index_above_cloud, 0
            ]

        # Continue with capture having prepared the new watermark at the cloud
        # and released from any watermarks above the cloud

        # Release and capture electrons all the way to watermarks below the cloud
        fill_fractions_old = self.watermarks_2d[: watermark_index_above_cloud + 1, 1:]
        self.watermarks_2d[: watermark_index_above_cloud + 1, 1:] = (
            fill_fractions_old * fill_probabilities_from_full_1d
            + (1 - fill_fractions_old) * fill_probabilities_from_empty_1d
        )

        # Collapse any redundant watermarks that are completely full
        (
            self.watermarks_2d,
            watermarks_initial_2d,
        ) = self.collapse_redundant_watermarks_with_copy(
            watermarks_2d=self.watermarks_2d, watermarks_copy_2d=watermarks_initial_2d
        )

        # Final number of electrons in traps
        n_trapped_electrons_final = self.n_trapped_electrons_from_watermarks(
            watermarks_2d=self.watermarks_2d
        )

        # Prevent division by zero errors
        if n_trapped_electrons_final == n_trapped_electrons_initial:
            return 0.0

        # Not enough available electrons to capture
        enough = n_free_electrons / (
            n_trapped_electrons_final - n_trapped_electrons_initial
        )
        if 0 < enough < 1:
            # For watermark fill fractions that increased, tweak them such that
            # the resulting increase instead matches the available electrons
            self.watermarks_2d = self.updated_watermarks_from_capture_not_enough(
                watermarks_2d=self.watermarks_2d,
                watermarks_initial_2d=watermarks_initial_2d,
                enough=enough,
            )

            # Final number of electrons in traps
            n_trapped_electrons_final = self.n_trapped_electrons_from_watermarks(
                watermarks_2d=self.watermarks_2d
            )

        # Collapse any redundant watermarks that are completely full
        self.watermarks_2d = self.collapse_redundant_watermarks_without_copy(
            watermarks_2d=self.watermarks_2d
        )

        return n_trapped_electrons_initial - n_trapped_electrons_final


class TrapManagerPhases:
    # def __init__(self, traps: Traps, max_n_transfer: int, ccd: CCD):
    #
    #     data = []  # type: t.List[TrapManager]
    #     for phase in range(ccd.n_phases):
    #
    #         trap_manager = TrapManager(traps, max_n_transfer)
    #
    #         trap_manager.n_traps_per_pixel = (
    #             trap_manager.n_traps_per_pixel * ccd.fraction_of_traps_per_phase[phase]
    #         )
    #
    #         data.append(trap_manager)
    #
    #     self.traps_managers = data  # type: t.Sequence[TrapManager]

    def __init__(self, trap_manager_phases: t.Sequence[TrapManager]):
        self.traps_managers = trap_manager_phases  # type: t.Sequence[TrapManager]

    def copy(self) -> "TrapManagerPhases":
        copied_data = []  # type: t.List[TrapManager]
        for trap_manager in self.traps_managers:  # type: TrapManager
            copied_data.append(trap_manager.copy())

        return TrapManagerPhases(copied_data)


def build_trap_manager_phases(
    traps: Traps, max_n_transfer: int, ccd: CCD
) -> TrapManagerPhases:

    data = []  # type: t.List[TrapManager]
    for phase in range(ccd.n_phases):
        trap_manager = TrapManager(traps, max_n_transfer)

        trap_manager.n_traps_per_pixel = (
            trap_manager.n_traps_per_pixel * ccd.fraction_of_traps_per_phase[phase]
        )

        data.append(trap_manager)

    return TrapManagerPhases(data)


class AllTrapManager:
    def __init__(
        self,
        traps_lst: t.Sequence[Traps],
        max_n_transfers: int,
        ccd: CCD,
    ):
        """
        A list (of a list) of trap managers.

        Each trap manager handles a group of trap species that shares watermark
        levels; these are joined in a list. The list is then repeated for each
        phase in the CCD pixels (default only 1), as the traps in each phase
        must be tracked separately. So each trap manager can be accessed as
        AllTrapManager[trap_group_index][phase].

        Parameters
        ----------
        traps : [[Trap]] (or Trap or [Trap])
            A list of one or more trap species. Species listed together in each
            innermost list must be able to share watermarks - i.e. they are
            distributed in the same way throughout the pixel volume and their
            state is stored in the same way by occupancy or time since filling,
            e.g.
            [
                [slow_trap, fast_trap],
                [continuum_lifetime_trap],
                [surface_trap],
            ]

        max_n_transfers : int
            The number of pixels containing traps that charge will be expected
            to move. This determines the maximum number of possible capture/
            release events that could create new watermark levels, and is used
            to initialise the watermark array to be only as large as needed, for
            efficiency.

        ccd : CCD
            Configuration of the CCD in which the electrons will move. Used to
            access the number of phases per pixel, and the fractional volume of
            a pixel that is filled by a cloud of electrons.

        Attributes
        ----------
        n_electrons_trapped_currently : float
            The number of electrons in traps that are currently being actively
            monitored.

        Methods
        -------
        empty_all_traps()
            Set all trap occupancies to empty.

        save()
            Save trap occupancy levels for future reference.

        restore()
            Recall trap occupancy levels.
        """
        # # Parse inputs
        # # If only a single trap species is supplied, still make sure it is a list
        # # if not isinstance(traps, list):
        # #     traps = [traps]
        # # if not isinstance(traps[0], list):
        # #     traps = [traps]
        # # traps = traps  # type: t.Sequence[t.Sequence[Trap]]
        #
        # # Replicate trap managers to keep track of traps in different phases separately
        # data = []  # type: t.List[t.List[TrapManager]]
        #
        # for phase in range(ccd.n_phases):
        #
        #     # Set up list of traps in a single phase of the CCD
        #     trap_managers_this_phase = []  # type: t.List[TrapManager]
        #
        #     for trap_group in traps:  # type: Traps
        #         # Use a non-default trap manager if required for the input trap species
        #         # if isinstance(
        #         #     trap_group[0],
        #         #     (TrapLifetimeContinuumAbstract, TrapLogNormalLifetimeContinuum),
        #         # ):
        #         #     trap_manager = TrapManagerTrackTime(
        #         #         traps=trap_group, max_n_transfers=max_n_transfers
        #         #     )
        #         # elif isinstance(trap_group[0], TrapInstantCapture):
        #         #     trap_manager = TrapManagerInstantCapture(
        #         #         traps=trap_group, max_n_transfers=max_n_transfers
        #         #     )
        #         # else:
        #         #     trap_manager = TrapManager(
        #         #         traps=trap_group, max_n_transfers=max_n_transfers
        #         #     )
        #
        #         # Removed keyword arguments because of Numba
        #         trap_manager = TrapManager(trap_group, max_n_transfers)
        #
        #         trap_manager.n_traps_per_pixel = (
        #             trap_manager.n_traps_per_pixel
        #             * ccd.fraction_of_traps_per_phase[phase]
        #         )
        #         trap_managers_this_phase.append(trap_manager)
        #
        #     data.append(trap_managers_this_phase)
        #
        # self.data = data
        #
        # # Initialise the empty trap state for future reference
        # self._saved_data = None  # type: t.Optional[t.List[t.List[TrapManager]]]
        # self._n_electrons_trapped_in_save = 0.0  # type: float
        # self._n_electrons_trapped_previously = 0.0  # type: float

        data = []  # type: t.List[TrapManagerPhases]

        for traps in traps_lst:  # type: Traps
            # trap_manager_phases = TrapManagerPhases(traps, max_n_transfers, ccd)
            trap_manager_phases = build_trap_manager_phases(
                traps, max_n_transfers, ccd
            )  # type: TrapManagerPhases
            data.append(trap_manager_phases)

        self.trap_manager_phases = data  # type: t.Sequence[TrapManagerPhases]

        # Initialise the empty trap state for future reference
        self._saved_trap_manager_phases = (
            None
        )  # type: t.Optional[t.List[TrapManagerPhases]]
        self._n_electrons_trapped_in_save = 0.0  # type: float
        self._n_electrons_trapped_previously = 0.0  # type: float

    @property
    def n_electrons_trapped_currently(self):
        """The number of electrons in traps that are currently being actively monitored."""
        # n_electrons_trapped_currently = 0.0  # type: float
        #
        # for trap_manager_phase in self.data:  # type: t.Sequence[TrapManager]
        #     for trap_manager in trap_manager_phase:  # type: TrapManager
        #         n_electrons_trapped_currently += (
        #             trap_manager.n_trapped_electrons_from_watermarks(
        #                 trap_manager.watermarks_2d
        #             )
        #         )
        #
        # return n_electrons_trapped_currently
        n_electrons_trapped_currently = 0.0  # type: float

        for trap_manager_phase in self.trap_manager_phases:  # type: TrapManagerPhases
            for trap_manager in trap_manager_phase.traps_managers:  # type: TrapManager
                n_electrons_trapped_currently += (
                    trap_manager.n_trapped_electrons_from_watermarks(
                        trap_manager.watermarks_2d
                    )
                )

        return n_electrons_trapped_currently

    def empty_all_traps(self):
        """Set all trap occupancies to zero"""
        # for trap_manager_phase in self.data:  # type: t.Sequence[TrapManager]
        #     for trap_manager_group in trap_manager_phase:  # type: TrapManager
        #         trap_manager_group.empty_all_traps()
        for trap_manager_phase in self.trap_manager_phases:  # type: TrapManagerPhases
            for (
                trap_manager_group
            ) in trap_manager_phase.traps_managers:  # type: TrapManager
                trap_manager_group.empty_all_traps()

    # TODO: Create a staticmethod
    def copy_trap_manager_phases(
        self, trap_manager_phases: t.Sequence[TrapManagerPhases]
    ) -> t.Sequence[TrapManagerPhases]:
        data = []  # type: t.List[TrapManagerPhases]
        for trap_manager_phase in trap_manager_phases:  # type: TrapManagerPhases
            data.append(trap_manager_phase.copy())

        return data

    def save(self):
        """Save trap occupancy levels for future reference"""
        # This stores far more than necessary. But extracting only the watermark
        # arrays requires overhead.

        # self._saved_data = deepcopy(self.data)
        # self._n_electrons_trapped_in_save = self.n_electrons_trapped_currently
        self._saved_trap_manager_phases = self.copy_trap_manager_phases(
            self.trap_manager_phases
        )
        self._n_electrons_trapped_in_save = self.n_electrons_trapped_currently

    def restore(self):
        """Restore trap occupancy levels"""
        # Book keeping, of how many electrons have ended up where.
        # About to forget about those currently in traps, so add them to previous total.
        # About to recall the ones in save back to current account, so remove them
        # from the savings.

        # self._n_electrons_trapped_previously += (
        #     self.n_electrons_trapped_currently - self._n_electrons_trapped_in_save
        # )
        # # Overwrite the current trap state
        # if self._saved_data is None:
        #     self.empty_all_traps()
        # else:
        #     self.data = deepcopy(self._saved_data)

        self._n_electrons_trapped_previously += (
            self.n_electrons_trapped_currently - self._n_electrons_trapped_in_save
        )
        # Overwrite the current trap state
        if self._saved_trap_manager_phases is None:
            self.empty_all_traps()
        else:
            self.trap_manager_phases = self.copy_trap_manager_phases(
                self._saved_trap_manager_phases
            )


def _clock_charge_in_one_direction(
    image_2d: np.ndarray,
    roe: ROE,
    ccd: CCD,
    traps: t.Sequence[Traps],
    express: int,
    offset: int,
    window_row_interval: t.Tuple[int, int],
    window_column_interval: t.Tuple[int, int],
    time_window_interval: t.Tuple[int, int],
) -> np.ndarray:
    """
    Add CTI trails to an image by trapping, releasing, and moving electrons
    along their independent columns.

    Parameters
    ----------
    image_2d : [[float]]
        The input array of pixel values, assumed to be in units of electrons.

        The first dimension is the "row" index, the second is the "column"
        index. By default (for parallel clocking), charge is transferred "up"
        from row n to row 0 along each independent column. i.e. the readout
        register is above row 0. (For serial clocking, the image is rotated
        beforehand, outside of this function, see add_cti().)

        e.g. (with arbitrary trap parameters)
        Initial image with one bright pixel in the first three columns:
            [[0.0,     0.0,     0.0,     0.0  ],
             [200.0,   0.0,     0.0,     0.0  ],
             [0.0,     200.0,   0.0,     0.0  ],
             [0.0,     0.0,     200.0,   0.0  ],
             [0.0,     0.0,     0.0,     0.0  ],
             [0.0,     0.0,     0.0,     0.0  ]]
        Final image with CTI trails behind each bright pixel:
            [[0.0,     0.0,     0.0,     0.0  ],
             [196.0,   0.0,     0.0,     0.0  ],
             [3.0,     194.1,   0.0,     0.0  ],
             [2.0,     3.9,     192.1,   0.0  ],
             [1.3,     2.5,     4.8,     0.0  ],
             [0.8,     1.5,     2.9,     0.0  ]]

    roe : ROE
        An object describing the timing and direction(s) in which electrons are
        moved during readout.

    ccd : CCD
        An object describing the way in which a cloud of electrons fills the CCD
        volume.

    traps : [Trap] or [[Trap]]
        A list of one or more trap objects. To use different types of traps that
        will require different watermark levels, pass a 2D list of lists, i.e. a
        list containing lists of one or more traps for each type.

    express : int
        The number of times the pixel-to-pixel transfers are computed,
        determining the balance between accuracy (high values) and speed
        (low values) (Massey et al. 2014, section 2.1.5).
            n_pix   (slower, accurate) Compute every pixel-to-pixel
                    transfer. The default 0 = alias for n_pix.
            k       Recompute on k occasions the effect of each transfer.
                    After a few transfers (and e.g. eroded leading edges),
                    the incremental effect of subsequent transfers can change.
            1       (faster, approximate) Compute the effect of each
                    transfer only once.
        Runtime scales approximately as O(express^0.5). ###WIP

    offset : int (>= 0)
        The number of (e.g. prescan) pixels separating the supplied image from
        the readout register.

    window_row_interval : range
        The subset of row pixels to model, to save time when only a specific
        region of the image is of interest. Defaults to range(0, n_pixels) for
        the full image.

    window_column_interval : range
        The subset of column pixels to model, to save time when only a specific
        region of the image is of interest. Defaults to range(0, n_columns) for
        the full image.

    time_window_interval : range
        The subset of transfers to implement. Defaults to range(0, n_pixels) for
        the full image. e.g. range(0, n_pixels/3) to do only the first third of
        the pixel-to-pixel transfers.

        The entire readout is still modelled, but only the results from this
        subset of transfers are implemented in the final image.

    Returns
    -------
    image : [[float]]
        The output array of pixel values.
    """

    # Generate the arrays over each step for: the number of of times that the
    # effect of each pixel-to-pixel transfer can be multiplied for the express
    # algorithm; and whether the traps must be monitored (usually whenever
    # express matrix > 0, unless using a time window)
    # Remove keyword arguments because of Numba
    (
        express_matrix_2d,
        monitor_traps_matrix_2d,
    ) = roe.express_matrix_and_monitor_traps_matrix_from_pixels_and_express(
        window_row_interval,
        express,
        offset,
        time_window_interval,
    )
    # ; and whether the trap occupancy states must be saved for the next express
    # pass rather than being reset (usually at the end of each express pass)
    # Remove keyword arguments because of Numba
    save_trap_states_matrix_2d = roe.save_trap_states_matrix_from_express_matrix(
        express_matrix_2d
    )  # type: np.ndarray

    n_express_pass, n_rows_to_process = express_matrix_2d.shape

    # Decide in advance which steps need to be evaluated and which can be skipped
    phases_with_traps = [
        i for i, frac in enumerate(ccd.fraction_of_traps_per_phase) if frac > 0
    ]  # type: t.Sequence[int]
    steps_with_nonzero_dwell_time = [
        i for i, time in enumerate(roe.dwell_times) if time > 0
    ]  # type: t.Sequence[int]

    # Set up the set of trap managers to monitor the occupancy of all trap species
    # if isinstance(roe, ROETrapPumping):
    #     # For trap pumping there is only one pixel and row to process but
    #     # multiple transfers back and forth without clearing the watermarks
    #     # Note, this allows for many more watermarks than are actually needed
    #     # in standard trap-pumping clock sequences
    #     max_n_transfers = n_express_pass * len(steps_with_nonzero_dwell_time)
    # else:
    #     max_n_transfers = n_rows_to_process * len(steps_with_nonzero_dwell_time)
    max_n_transfers = n_rows_to_process * len(
        steps_with_nonzero_dwell_time
    )  # type: int

    trap_managers = AllTrapManager(
        traps_lst=traps, max_n_transfers=max_n_transfers, ccd=ccd
    )

    # Temporarily expand image, if charge released from traps ever migrates to
    # a different charge packet, at any time during the clocking sequence
    n_rows_zero_padding = max(roe.pixels_accessed_during_clocking_1d) - min(
        roe.pixels_accessed_during_clocking_1d
    )  # type: int
    zero_padding_2d = np.zeros(
        (n_rows_zero_padding, image_2d.shape[1]), dtype=image_2d.dtype
    )
    image_2d = np.concatenate((image_2d, zero_padding_2d), axis=0)

    window_column_range = range(window_column_interval[0], window_column_interval[1])
    window_row_range = range(window_row_interval[0], window_row_interval[1])

    # Read out one column of pixels through the (column of) traps
    for column_index in window_column_range:
        # Monitor the traps in every pixel, or just one (express=1) or a few
        # (express=a few) then replicate their effect
        for express_index in range(n_express_pass):
            # Restore the trap occupancy levels (to empty, or to a saved state
            # from a previous express pass)
            trap_managers.restore()

            # Each pixel
            for row_index in range(len(window_row_range)):
                express_multiplier = express_matrix_2d[
                    express_index, row_index
                ]  # type: float
                # Skip this step if not needed to be evaluated (may need to
                # monitor the traps and update their occupancies even if
                # express_mulitplier is 0, e.g. for a time window)
                if not monitor_traps_matrix_2d[express_index, row_index]:
                    continue

                for clocking_step in steps_with_nonzero_dwell_time:

                    for phase in phases_with_traps:
                        # Information about the potentials in this phase
                        roe_phase = roe.clock_sequence[clocking_step][
                            phase
                        ]  # type: ROEPhase

                        # Select the relevant pixel (and phase) for the initial charge
                        row_index_read_1d = int(
                            window_row_range[row_index]
                            + roe_phase.capture_from_which_pixels_1d
                        )  # type: int

                        # Initial charge (0 if this phase's potential is not high)
                        n_free_electrons = (
                            image_2d[row_index_read_1d, column_index]
                            * roe_phase.is_high
                        )  # type: float

                        # Allow electrons to be released from and captured by traps
                        n_electrons_released_and_captured = 0.0  # type: float
                        # for trap_manager in trap_managers.data[
                        #     phase
                        # ]:  # type: TrapManager
                        #
                        #     # Remove keyword arguments because of Numba
                        #     value = trap_manager.n_electrons_released_and_captured(
                        #         n_free_electrons,
                        #         ccd,
                        #         phase,
                        #         # ccd_filling_function=ccd.well_filling_function(
                        #         #     phase=phase
                        #         # ),
                        #         roe.dwell_times[clocking_step],
                        #         express_multiplier,
                        #     )
                        #
                        #     n_electrons_released_and_captured += value
                        for (
                            trap_manager_phase
                        ) in (
                            trap_managers.trap_manager_phases
                        ):  # type: TrapManagerPhases
                            trap_manager = trap_manager_phase.traps_managers[
                                phase
                            ]  # type: TrapManager

                            # Remove keyword arguments because of Numba
                            value = trap_manager.n_electrons_released_and_captured(
                                n_free_electrons,
                                ccd,
                                phase,
                                # ccd_filling_function=ccd.well_filling_function(
                                #     phase=phase
                                # ),
                                roe.dwell_times[clocking_step],
                                express_multiplier,
                            )

                            n_electrons_released_and_captured += value

                        # Skip updating the image if only monitoring the traps
                        if express_multiplier == 0.0:
                            continue

                        # Select the relevant pixel (and phase(s)) for the returned charge
                        row_index_write_1d = (
                            window_row_range[row_index]
                            + roe_phase.release_to_which_pixels_1d
                        )  # type: np.ndarray

                        # Return the electrons back to the relevant charge
                        # cloud, or a fraction if they are being returned to
                        # multiple phases
                        image_2d[row_index_write_1d, column_index] += (
                            n_electrons_released_and_captured
                            * roe_phase.release_fraction_to_pixel_1d
                            * express_multiplier
                        )

                        # Make sure image counts don't go negative, as could
                        # otherwise happen with a too-large express_multiplier
                        for row_index_single in row_index_write_1d:
                            if image_2d[row_index_single, column_index] < 0.0:
                                image_2d[row_index_single, column_index] = 0.0

                # Save the trap occupancy states for the next express pass
                if save_trap_states_matrix_2d[express_index, row_index]:
                    trap_managers.save()

        # Reset the watermarks for the next column, effectively setting the trap
        # occupancies to zero
        if roe.empty_traps_between_columns:
            trap_managers.empty_all_traps()
        trap_managers.save()

    # Unexpand the image to its original dimensions
    if n_rows_zero_padding > 0:
        image_2d = image_2d[0:-n_rows_zero_padding, :]

    return image_2d


def add_cti(
    image_2d: np.ndarray,
    parallel_ccd: CCD,
    parallel_roe: ROE,
    parallel_traps: t.Sequence[Traps],
    parallel_express: int = 0,
    parallel_offset: int = 0,
    parallel_window_range: t.Optional[t.Tuple[int, int]] = None,
    # serial_ccd=None,
    # serial_roe: ROE,
    # serial_traps=None,
    # serial_express=0,
    # serial_offset=0,
    serial_window_range: t.Optional[t.Tuple[int, int]] = None,
    time_window_range: t.Optional[t.Tuple[int, int]] = None,
):
    """
    Add CTI trails to an image by trapping, releasing, and moving electrons
    along their independent columns, for parallel and/or serial clocking.

    Parameters
    ----------
    image_2d : [[float]] or frames.Frame
        The input array of pixel values, assumed to be in units of electrons.

        The first dimension is the "row" index, the second is the "column"
        index. By default (for parallel clocking), charge is transfered "up"
        from row n to row 0 along each independent column. i.e. the readout
        register is above row 0. (For serial clocking, the image is rotated
        before modelling, such that charge moves from column n to column 0.)

        e.g. (with arbitrary trap parameters)
        Initial image with one bright pixel in the first three columns:
            [[0.0,     0.0,     0.0,     0.0  ],
             [200.0,   0.0,     0.0,     0.0  ],
             [0.0,     200.0,   0.0,     0.0  ],
             [0.0,     0.0,     200.0,   0.0  ],
             [0.0,     0.0,     0.0,     0.0  ],
             [0.0,     0.0,     0.0,     0.0  ]]
        Image with parallel CTI trails:
            [[0.0,     0.0,     0.0,     0.0  ],
             [196.0,   0.0,     0.0,     0.0  ],
             [3.0,     194.1,   0.0,     0.0  ],
             [2.0,     3.9,     192.1,   0.0  ],
             [1.3,     2.5,     4.8,     0.0  ],
             [0.8,     1.5,     2.9,     0.0  ]]
        Final image with parallel and serial CTI trails:
            [[0.0,     0.0,     0.0,     0.0  ],
             [194.1,   1.9,     1.5,     0.9  ],
             [2.9,     190.3,   2.9,     1.9  ],
             [1.9,     3.8,     186.5,   3.7  ],
             [1.2,     2.4,     4.7,     0.9  ],
             [0.7,     1.4,     2.8,     0.6  ]]

    parallel_express : int
        The number of times the transfers are computed, determining the
        balance between accuracy (high values) and speed (low values), for
        parallel clocking (Massey et al. 2014, section 2.1.5).

    parallel_roe : ROE
        The object describing the clocking read-out electronics for parallel
        clocking.

    parallel_ccd : CCD
        The object describing the CCD volume for parallel clocking. For
        multi-phase clocking optionally use a list of different CCD volumes
        for each phase, in the same size list as parallel_roe.dwell_times.

    parallel_traps : [Trap] or [[Trap]]
        A list of one or more trap objects for parallel clocking. To use
        different types of traps that will require different watermark
        levels, pass a 2D list of lists, i.e. a list containing lists of
        one or more traps for each type.

    parallel_offset : int (>= 0)
        The number of (e.g. prescan) pixels separating the supplied image from
        the readout register. i.e. Treat the input image as a sub-image that is
        offset this number of pixels from readout, increasing the number of
        pixel-to-pixel transfers.

    parallel_window_range : range
        For speed, calculate only the effect on this subset of pixels. Defaults
        to range(0, n_pixels) for the full image.

        Note that, because of edge effects, the range should be started several
        pixels before the actual region of interest.

        For a single pixel (e.g. for trap pumping), can enter just the single
        integer index of the pumping traps to monitor, which will be converted
        to range(index, index + 1).

    serial_* : *
        The same as the parallel_* objects described above but for serial
        clocking instead.

    time_window_range : range
        The subset of transfers to implement. Defaults to range(0, n_pixels) for
        the full image. e.g. range(0, n_pixels/3) to do only the first third of
        the pixel-to-pixel transfers.

        The entire readout is still modelled, but only the results from this
        subset of transfers are implemented in the final image.

        This could be used to e.g. add cosmic rays during readout of simulated
        images. Successive calls to complete the readout should start at
        the same value that the previous one ended, e.g. range(0, 1000) then
        range(1000, 2000). Be careful not to divide the readout too finely, as
        there is only as much temporal resolution as there are rows (not rows *
        phases) in the image. Also, for each time that readout is split between
        successive calls to this function, the output in one row of pixels
        will change slightly (unless express=0) because trap occupancy is
        not stored between calls.

    Returns
    -------
    image : [[float]] or frames.Frame
        The output array of pixel values.
    """
    n_rows_in_image, n_columns_in_image = image_2d.shape

    # Default windows to the full image; convert single-pixel windows to ranges
    if parallel_window_range is None:
        parallel_window_range_start, parallel_window_range_stop = 0, n_rows_in_image
    # elif isinstance(parallel_window_range, int):
    #     parallel_window_range = range(parallel_window_range, parallel_window_range + 1)

    if serial_window_range is None:
        serial_window_range_start, serial_window_range_stop = 0, n_columns_in_image
    # elif isinstance(serial_window_range, int):
    #     serial_window_range = range(serial_window_range, serial_window_range + 1)

    if time_window_range is None:
        # time_window_range = range(n_rows_in_image + parallel_offset)
        time_window_range_start, time_window_range_stop = (
            0,
            n_rows_in_image + parallel_offset,
        )

        # Set the "columns" window in the rotated image for serial clocking
        # serial_window_column_range = parallel_window_range
        serial_window_column_range_start, serial_window_column_range_stop = (
            parallel_window_range_start,
            parallel_window_range_stop,
        )

    else:
        raise NotImplementedError
        # Intersection of spatial and time windows for serial clocking
        # serial_window_column_range = range(
        #     int(max(parallel_window_range[0], time_window_range[0] - parallel_offset)),
        #     int(min(parallel_window_range[-1], time_window_range[-1] - parallel_offset))
        #     + 1,
        # )

    # Default ROE: simple, single-phase clocking in imaging mode
    # if parallel_roe is None:
    #     parallel_roe = ROE()
    # if serial_roe is None:
    #     serial_roe = ROE()

    # Don't modify the external array passed to this function
    # image_add_cti = deepcopy(image)
    image_add_cti_2d = image_2d.copy()  # type: np.ndarray

    # Parallel clocking
    if parallel_traps is not None:
        # Transfer charge in parallel direction
        image_add_cti_2d = _clock_charge_in_one_direction(
            image_2d=image_add_cti_2d,
            ccd=parallel_ccd,
            roe=parallel_roe,
            traps=parallel_traps,
            express=parallel_express,
            offset=parallel_offset,
            window_row_interval=(
                parallel_window_range_start,
                parallel_window_range_stop,
            ),
            window_column_interval=(
                serial_window_range_start,
                serial_window_range_stop,
            ),
            time_window_interval=(time_window_range_start, time_window_range_stop),
        )

    # Serial clocking
    # if serial_traps is not None:
    #     # Switch axes, so clocking happens in other direction
    #     image_add_cti_2d = image_add_cti_2d.T.copy()
    #
    #     # Transfer charge in serial direction
    #     image_add_cti_2d = _clock_charge_in_one_direction(
    #         image=image_add_cti_2d,
    #         ccd=serial_ccd,
    #         roe=serial_roe,
    #         traps=serial_traps,
    #         express=serial_express,
    #         offset=serial_offset,
    #         window_row_range=serial_window_range,
    #         window_column_range=serial_window_column_range,
    #         time_window_range=None,
    #     )
    #
    #     # Switch axes back
    #     image_add_cti_2d = image_add_cti_2d.T

    # TODO : Implement as decorator

    # if isinstance(image_2d, frames.Frame):
    #     return image_2d.__class__(
    #         array=image_add_cti_2d,
    #         mask=image_2d.mask,
    #         original_roe_corner=image_2d.original_roe_corner,
    #         scans=image_2d.scans,
    #         exposure_info=image_2d.exposure_info,
    #     )

    return image_add_cti_2d


def arctic_no_numba(
    detector: PyxelCCD,
    well_fill_power: float,
    density: float,
    release_timescale: t.Sequence[float],
    express: int = 0,
) -> np.ndarray:

    char = detector.characteristics
    image_2d = detector.pixel.array
    image_2d = image_2d.astype(float)

    ccd = CCD(
        n_phases=1,
        fraction_of_traps_per_phase=np.array([1.0], dtype=np.float64),
        full_well_depth=np.array([char.fwc], dtype=np.float64),
        well_notch_depth=np.array([0.0], dtype=np.float64),
        well_fill_power=np.array([well_fill_power], dtype=np.float64),
        well_bloom_level=np.array([char.fwc], dtype=np.float64),
    )

    parallel_roe = ROE(dwell_times=np.array([1.0], dtype=np.float64))
    # serial_roe = ROE(dwell_times=np.array([1.0], dtype=np.float64))
    # trap = Trap(density=density, release_timescale=release_timescale)

    traps = Traps(
        density_1d=np.array([density], dtype=np.float64),
        release_timescale_1d=np.array([release_timescale], dtype=np.float64),
        capture_timescale_1d=np.array([0.0], dtype=np.float64),
        surface_1d=np.array([False], dtype=np.bool_),
    )

    s = add_cti(
        image_2d=image_2d,
        parallel_traps=[traps],
        parallel_ccd=ccd,
        parallel_roe=parallel_roe,
        parallel_express=express,
        # serial_roe=serial_roe,
    )

    detector.pixel.array = s
    return s
