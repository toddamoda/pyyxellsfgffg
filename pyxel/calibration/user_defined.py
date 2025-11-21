#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Subpackage containing user defined Island and Batch Fitness evaluator using Dask."""

import logging
from typing import TYPE_CHECKING

import numpy as np
from dask import array as da
from dask.delayed import Delayed, delayed

if TYPE_CHECKING:
    import pygmo as pg

__all__ = ["DaskBFE", "DaskIsland"]


class DaskBFE:
    """User defined Batch Fitness Evaluator using `Dask`.

    This class is a user-defined batch fitness evaluator based on 'Dask'.
    """

    def __init__(self, chunk_size: int | None = None):
        self._chunk_size = chunk_size

    def __call__(self, prob: "pg.problem", dvs_1d: np.ndarray) -> np.ndarray:
        """Call operator to run the batch fitness evaluator.

        Parameters
        ----------
        prob
        dvs_1d

        Returns
        -------
        array_like
            A 1d array with the fitness parameters.
        """
        try:
            # Get dimensions of the problem and the fitness
            ndims_dvs: int = prob.get_nx()
            num_fitness: int = prob.get_nf()

            if self._chunk_size is None:
                chunk_size: int = max(1, num_fitness // 10)
            else:
                chunk_size = self._chunk_size

            # [dvs_1_1, ..., dvs_1_n, dvs_2_1, ..., dvs_2_n, ..., dvs_m_1, ..., dvs_m_n]

            # [[dvs_1_1, ..., dvs_1_n],
            #  [dvs_2_1, ..., dvs_2_n],
            #  ...
            #  [dvs_m_1, ..., dvs_m_n]]

            # Convert 1D Decision Vectors to 2D `dask.Array`
            dvs_2d: da.Array = da.from_array(
                dvs_1d.reshape((-1, ndims_dvs)),
                chunks=(chunk_size, ndims_dvs),
            )

            logging.info("DaskBFE: %i, %i, %r", len(dvs_1d), ndims_dvs, dvs_2d.shape)

            # Create a generalized function to run a 2D input with 'prob.fitness'
            fitness_func = da.gufunc(
                prob.fitness,
                signature="(i)->(j)",
                output_dtypes=float,
                output_sizes={"j": num_fitness},
                vectorize=True,
            )

            fitness_2d: da.Array = fitness_func(dvs_2d)
            fitness_1d: da.Array = fitness_2d.ravel()

            final_fitness_1d = np.array(fitness_1d)

        except Exception:
            logging.exception("Caught an exception in 'fitness' for ModelFitting.")
            raise

        else:
            return final_fitness_1d

    def get_name(self) -> str:
        """Return name of this evaluator."""
        return "Dask batch fitness evaluator"

    def get_extra_info(self) -> str:
        """Return extra information for this evaluator."""
        return f"Dask batch fitness evaluator with chunk_size={self._chunk_size}."


class DaskIsland:
    """User Defined Island using `Dask`."""

    def run_evolve(
        self, algo: "pg.algorithm", pop: "pg.population"
    ) -> tuple["pg.algorithm", "pg.population"]:
        """Run 'evolve' method from the input `algorithm` to evolve the input `population`.

        Once the evolution is finished, it will return the algorithm used for the
        evolution and the evolved `population`.

        Parameters
        ----------
        algo : pg.algorithm
            Algorithm used to evolve the input population
        pop : pg.population
            Input population.

        Returns
        -------
        tuple of pg.algorithm, pg.population
            The algorithm used for the evolution and the evolved population.
        """
        logging.info("Run evolve %r, %r", pop, algo)

        # Run 'algo.evolve' with `Dask`
        delayed_pop: Delayed = delayed(pop)
        delayed_result: Delayed = delayed(algo.evolve)(delayed_pop)

        new_pop: pg.population = delayed_result.compute()
        return algo, new_pop

    def get_name(self) -> str:
        """Return Island's name."""
        return "Dask Island"
