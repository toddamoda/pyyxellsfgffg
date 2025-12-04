#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Sub-package to create 'archipelagos'."""

import logging
from collections.abc import Callable, Sequence
from concurrent.futures.thread import ThreadPoolExecutor
from pathlib import Path
from timeit import default_timer as timer
from typing import TYPE_CHECKING

import dask.array as da
import numpy as np
import pandas as pd
import xarray as xr
from tqdm.auto import tqdm
from typing_extensions import deprecated

from pyxel.calibration import Algorithm, IslandProtocol
from pyxel.calibration.fitting_datatree import ModelFittingDataTree
from pyxel.calibration.util import slice_to_range

if TYPE_CHECKING:
    import pygmo as pg
    from dask.delayed import Delayed
    from numpy.typing import ArrayLike

    from pyxel.exposure import Readout


def extract_data_3d(
    df_results: pd.DataFrame,
    rows: int,
    cols: int,
    times: int,
    readout_times: np.ndarray,
) -> xr.Dataset:
    """Extract 'photon', 'charge', 'pixel', 'signal' and 'image' arrays from several delayed dynamic results."""
    lst: list[xr.Dataset] = []
    for _, row in df_results.iterrows():
        island: int = row["island"]
        id_processor: int = row["id_processor"]
        data_tree: Delayed = row["data_tree"]

        photon_delayed: Delayed = data_tree["photon"]  # type: ignore
        charge_delayed: Delayed = data_tree["charge"]  # type: ignore
        pixel_delayed: Delayed = data_tree["pixel"]  # type: ignore
        signal_delayed: Delayed = data_tree["signal"]  # type: ignore
        image_delayed: Delayed = data_tree["image"]  # type: ignore

        photon_3d = da.from_delayed(
            photon_delayed, shape=(times, rows, cols), dtype=float
        )
        charge_3d = da.from_delayed(
            charge_delayed, shape=(times, rows, cols), dtype=float
        )
        pixel_3d = da.from_delayed(
            pixel_delayed, shape=(times, rows, cols), dtype=float
        )
        signal_3d = da.from_delayed(
            signal_delayed, shape=(times, rows, cols), dtype=float
        )
        image_3d = da.from_delayed(
            image_delayed, shape=(times, rows, cols), dtype=float
        )

        partial_ds = xr.Dataset()
        partial_ds["simulated_photon"] = xr.DataArray(
            photon_3d, dims=["readout_time", "y", "x"]
        )
        partial_ds["simulated_charge"] = xr.DataArray(
            charge_3d, dims=["readout_time", "y", "x"]
        )
        partial_ds["simulated_pixel"] = xr.DataArray(
            pixel_3d, dims=["readout_time", "y", "x"]
        )
        partial_ds["simulated_signal"] = xr.DataArray(
            signal_3d, dims=["readout_time", "y", "x"]
        )
        partial_ds["simulated_image"] = xr.DataArray(
            image_3d, dims=["readout_time", "y", "x"]
        )

        lst.append(
            partial_ds.assign_coords(
                island=island,
                id_processor=id_processor,
            ).expand_dims(["island", "id_processor"])
        )

    ds: xr.Dataset | xr.DataArray = xr.combine_by_coords(lst).assign_coords(
        readout_time=readout_times,
        y=range(rows),
        x=range(cols),
    )

    if not isinstance(ds, xr.Dataset):
        raise TypeError("Expected a Dataset.")

    return ds


# TODO: Rename to PyxelArchipelago. See #335
class ArchipelagoDataTree:
    """User-defined Archipelago."""

    def __init__(
        self,
        num_islands: int,
        udi: IslandProtocol,
        algorithm: Algorithm,
        problem: ModelFittingDataTree,
        pop_size: int,
        output_folder: Path | None = None,
        bfe: Callable | None = None,
        topology: Callable | None = None,
        pygmo_seed: int | None = None,
        parallel: bool = True,
        with_bar: bool = False,
    ):
        try:
            import pygmo as pg
        except ModuleNotFoundError as exc:
            raise ModuleNotFoundError(
                "Missing optional package 'pygmo'.\n"
                "Please install it with 'pip install pyxel-sim[calibration]' "
                "or 'pip install pyxel-sim[all]'"
            ) from exc

        self._log = logging.getLogger(__name__)

        self.num_islands = num_islands
        self.udi = udi
        self.algorithm: Algorithm = algorithm
        self.problem: ModelFittingDataTree = problem
        self.pop_size = pop_size
        self._output_folder: Path | None = output_folder
        self.bfe = bfe
        self.topology = topology
        self.pygmo_seed = pygmo_seed
        self.parallel = parallel
        self.with_bar = with_bar

        # Create a Pygmo archipelago
        self._pygmo_archi = pg.archipelago(t=self.topology)

        # Create a Pygmo algorithm
        verbosity_level: int = max(1, self.algorithm.population_size // 100)

        self._pygmo_algo: pg.algorithm = pg.algorithm(self.algorithm.get_algorithm())
        self._pygmo_algo.set_verbosity(verbosity_level)
        self._log.info(self._pygmo_algo)

        # Create a Pygmo problem
        self._pygmo_prob: pg.problem = pg.problem(self.problem)
        self._log.info(self._pygmo_prob)

        # Build the archipelago
        self._build()

    def _build(self) -> None:
        """Build the island(s) and populate them."""
        import pygmo as pg

        disable_bar: bool = not self.with_bar
        start_time: float = timer()

        def create_island(seed: int | None = None) -> pg.island:
            """Create a new island."""
            return pg.island(
                udi=self.udi,
                algo=self._pygmo_algo,
                prob=self._pygmo_prob,
                b=self.bfe,
                size=self.pop_size,
                seed=seed,
            )

        # Create a seed for each island
        if self.pygmo_seed is None:
            seeds: Sequence[int | None] = [None] * self.num_islands
        else:
            rng: np.random.Generator = np.random.default_rng(seed=self.pygmo_seed)
            max_value: int = np.iinfo(np.uint32).max
            seeds = [int(rng.integers(0, max_value)) for _ in range(self.num_islands)]

        # Create the islands and add them to this archipelago
        if self.parallel:
            # Create the islands in parallel with Threads
            with ThreadPoolExecutor(max_workers=self.num_islands) as executor:
                it = executor.map(create_island, seeds)

                for island in tqdm(
                    it,
                    desc="Create islands",
                    total=self.num_islands,
                    disable=disable_bar,
                ):
                    self._pygmo_archi.push_back(island)
        else:
            # Create the islands sequentially
            it = map(create_island, seeds)
            for island in tqdm(
                it,
                desc="Create islands",
                total=self.num_islands,
                disable=disable_bar,
            ):
                self._pygmo_archi.push_back(island)

        stop_time = timer()
        logging.info("Create a new archipelago in %.2f s", stop_time - start_time)

    def run_evolve(
        self,
        readout: "Readout",
        num_rows: int,
        num_cols: int,
        num_evolutions: int = 1,
        num_best_decisions: int | None = None,
    ) -> xr.DataTree:
        """Run evolution(s) several time.

        Parameters
        ----------
        readout : Readout
        num_rows : int
        num_cols : int
        num_evolutions : int
            Number of time to run the evolutions.
        num_best_decisions : int or None, optional.
            Number of best individuals to extract. If this parameter is set to None then
            no individuals are extracted.

        Returns
        -------
        DataTree
        """
        # Late import
        from pyxel.outputs.utils import to_netcdf

        self._log.info("Run %i evolutions", num_evolutions)

        total_num_generations = num_evolutions * self.algorithm.generations

        with tqdm(
            total=total_num_generations,
            desc=f"Evolve with {self.num_islands} islands",
            unit=" generations",
            disable=not self.with_bar,
        ) as progress:
            champions_lst: list[xr.Dataset] = []
            best_population_lst: list[xr.Dataset] = []

            # Run an evolution im the archipelago several times
            for id_evolution in range(num_evolutions):
                # If the evolution on this archipelago was already run before, then
                # the migration process between the islands is automatically executed
                # Call all 'evolve()' methods on all islands
                self._pygmo_archi.evolve()
                # self._log.info(self._pygmo_archi)  # TODO: Remove this

                # Block until all evolutions have finished and raise the first exception
                # that was encountered
                self._pygmo_archi.wait_check()

                progress.update(self.algorithm.generations)

                # Get partial champions for this evolution
                champions_partial: xr.Dataset = self._get_champions()

                # Get full and best population from all islands
                ds_full_population, ds_best_population = self._get_population(
                    num_best_decisions=num_best_decisions,
                    full_population=True,
                )
                if ds_full_population and self._output_folder:
                    # Save the population into a netcdf file, send to grafana, bokeh, ...
                    filename = to_netcdf(
                        current_output_folder=self._output_folder,
                        data=ds_full_population,
                        name=f"population_{id_evolution:02d}",
                    )
                    self._log.info("Population saved in %s", filename)

                champions_lst.append(
                    champions_partial.assign_coords(evolution=id_evolution)
                )

                if ds_best_population:
                    best_population_lst.append(
                        ds_best_population.assign_coords(evolution=id_evolution)
                    )

        # Get all champions
        champions: xr.Dataset = xr.concat(champions_lst, dim="evolution")
        best_population: xr.Dataset = xr.concat(best_population_lst, dim="evolution")

        # Get the champions in a `Dataset`
        last_champions = champions.isel(evolution=-1)

        # Get the processor(s) in a `DataFrame`
        df_results: pd.DataFrame = self.problem.apply_parameters_to_processors(
            parameters=last_champions["champion_parameters"],
        )

        num_times = len(readout.times)

        # Extract simulated 'image', 'signal' and 'pixel' from the processors
        all_simulated_full: xr.Dataset = extract_data_3d(
            df_results=df_results,
            rows=num_rows,
            cols=num_cols,
            times=num_times,
            readout_times=readout.times,
        ).rename(id_processor="processor")

        # Get the target data
        if self.problem.sim_fit_range is not None:
            slice_times, slice_rows, slice_cols = self.problem.sim_fit_range.to_slices()

            sim_fit_range_dct: dict[str, slice] = dict(
                self.problem.sim_fit_range.to_dict()
            )
            if time_value := sim_fit_range_dct.get("time"):  # TODO: Fix this
                sim_fit_range_dct["readout_time"] = time_value
                del sim_fit_range_dct["time"]

            all_data_fit_range = all_simulated_full.isel(indexers=sim_fit_range_dct)
            if readout.time_domain_simulation:
                # TODO: Refactoring like this:
                #       all_data_fit_range["target"] = self.problem.all_target_data
                all_data_fit_range["target"] = xr.DataArray(
                    self.problem.all_target_data,
                    dims=["processor", "readout_time", "y", "x"],
                    coords={
                        "processor": range(len(self.problem.all_target_data)),
                        "readout_time": slice_to_range(slice_times),
                        "y": slice_to_range(slice_rows),
                        "x": slice_to_range(slice_cols),
                    },
                )
            else:
                all_data_fit_range["target"] = self.problem.all_target_data

        else:
            all_data_fit_range = all_simulated_full
            all_data_fit_range["target"] = self.problem.all_target_data

        data_tree: xr.DataTree = xr.DataTree.from_dict(
            {
                "/champion": champions,
                "/best": best_population,
                "/simulated": all_data_fit_range,
                "/full_size": all_simulated_full,
            }
        )
        data_tree["/full_size/target"] = self.problem.target_full_scale

        data_tree.attrs["num_islands"] = self.num_islands
        data_tree.attrs["population_size"] = self.algorithm.population_size
        data_tree.attrs["num_evolutions"] = num_evolutions
        data_tree.attrs["generations"] = self.algorithm.generations

        return data_tree

    def _get_champions(self) -> xr.Dataset:
        """Extract the champions.

        Returns
        -------
        Dataset
            A dataset containing the champions.

        Examples
        --------
        >>> self._get_champions()
        <xarray.Dataset>
        Dimensions:              (island: 2, param_id: 7)
        Dimensions without coordinates: island, param_id
        Data variables:
            champion_fitness     (island) float64 3.285e+04 4.102e+04
            champion_decision    (island, param_id) float64 0.1526 -1.977 ... 0.9329
            champion_parameters  (island, param_id) float64 0.1526 -1.977 ... 8.568
        """
        # Get fitness and decision vectors of the num_islands' champions
        champions_1d_fitness: ArrayLike = self._pygmo_archi.get_champions_f()
        champions_2d_decision: ArrayLike = self._pygmo_archi.get_champions_x()

        # Get the champions as a Dataset
        champions = xr.Dataset()
        champions["champion_fitness"] = xr.DataArray(
            np.ravel(champions_1d_fitness), dims="island"
        )
        champions["champion_decision"] = xr.DataArray(
            champions_2d_decision, dims=["island", "param_id"]
        )
        champions["champion_parameters"] = xr.DataArray(
            self.problem.convert_to_parameters(champions["champion_decision"]),
            dims=["island", "param_id"],
        )

        num_islands, num_params = champions["champion_decision"].shape

        return champions.assign_coords(
            island=range(num_islands), param_id=range(num_params)
        )

    def get_population_per_island(self, island: "pg.island") -> xr.Dataset:
        population: pg.population = island.get_population()

        # Get the decision vectors: num_individuals x size_decision_vector
        decision_2d: np.ndarray = population.get_x()

        # Get the fitness vectors: num_individuals x 1
        fitness_2d: np.ndarray = population.get_f()

        # Convert the decision vectors to parameters:
        #   num_individuals x size_decision_vector
        parameters_2d = self.problem.convert_to_parameters(decision_2d)

        # Get the full population
        ds = xr.Dataset()
        ds["decision"] = xr.DataArray(decision_2d, dims=["individual", "param_id"])
        ds["parameters"] = xr.DataArray(parameters_2d, dims=["individual", "param_id"])
        ds["fitness"] = xr.DataArray(fitness_2d.flatten(), dims=["individual"])

        num_individuals, num_params_id = decision_2d.shape

        return ds.assign_coords(
            individual=range(num_individuals), param_id=range(num_params_id)
        )

    def _get_population(
        self,
        num_best_decisions: int | None,
        full_population: bool,
    ) -> tuple[xr.Dataset, xr.Dataset]:
        full_population_lst: list[xr.Dataset] = []
        best_population_lst: list[xr.Dataset] = []

        if not num_best_decisions and not full_population:
            return xr.Dataset(), xr.Dataset()

        for island_idx, island in enumerate(self._pygmo_archi):
            ds_full_population = self.get_population_per_island(island).assign_coords(
                island=island_idx
            )

            if full_population:
                full_population_lst.append(ds_full_population)

            if num_best_decisions is not None and num_best_decisions > 1:
                best_population_lst.append(
                    ds_full_population.sortby("fitness")
                    .isel(individual=slice(num_best_decisions))
                    .assign_coords(individual=range(num_best_decisions))
                )

        ds_full_population = xr.concat(full_population_lst, dim="island")

        if num_best_decisions == -1:
            ds_best_population = ds_full_population
        else:
            ds_best_population = xr.concat(best_population_lst, dim="island")

        return ds_full_population, ds_best_population

    @deprecated("This method will be removed")
    def get_best_individuals(self, num_best_decisions: int) -> xr.Dataset:
        """Get the best decision vectors and fitness from the island of an archipelago.

        Parameters
        ----------
        num_best_decisions : int or None, optional.
            Number of best individuals to extract. If this parameter is set to None then
            no individuals are extracted.

        Returns
        -------
        Dataset
            A new dataset with two data arrays 'best_decision' and 'best_fitness'.

        Examples
        --------
        >>> archi = MyArchipelago(...)
        >>> archi.get_best_individuals(num_best_decisions=5)
        <xarray.Dataset>
        Dimensions:          (individual: 10, island: 2, param_id: 7)
        Coordinates:
          * island           (island) int64 0 1
          * individual       (individual) int64 0 1 2 3 4 5 6 7 8 9
        Dimensions without coordinates: param_id
        Data variables:
            best_decision    (island, individual, param_id) float64 0.1526 ... 0.1608
            best_parameters  (island, individual, param_id) float64 0.1526 ... 0.1608
            best_fitness     (island, individual) float64 3.285e+04 ... 5.732e+04

        Raises
        ------
        ValueError
            Raised if 'num_best_decisions' is a negative 'int' value.
        """
        if num_best_decisions < 0:
            raise ValueError(
                "'num_best_decisions' must be 'None' or a positive integer"
            )

        lst = []
        for island_idx, island in enumerate(self._pygmo_archi):
            # Get the population of the whole island
            ds_population: xr.Dataset = self.get_population_per_island(island)

            # Get the best 'num_best_decisions'
            ds_best_individuals = (
                ds_population.sortby(ds_population["fitness"])
                .isel(individual=slice(num_best_decisions))
                .assign_coords(island=island_idx)
            )

            lst.append(ds_best_individuals)

        # Create a new dataset
        best_individuals_no_coordinates = xr.concat(lst, dim="island")

        # Add coordinates
        num_individuals = len(best_individuals_no_coordinates["individual"])
        best_individuals: xr.Dataset = best_individuals_no_coordinates.assign_coords(
            individual=range(num_individuals),
            island=range(len(self._pygmo_archi)),
        )

        return best_individuals
