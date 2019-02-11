.. _running_modes:

Running Pyxel
==============

To run Pyxel on your local computer, simply run it from the command-line:

.. code-block:: bash

  python pyxel/run.py
         -c pyxel/io/config/input.yaml
         -o output_folder
         -s 1234

where

======  ===============  =======================================  ==========
``-c``  ``--config``     defines the path of the input YAML file  compulsory
``-s``  ``--seed``       defines a seed for random number         optional
                         generator
``-v``  ``--verbosity``  increases the output verbosity           optional
``-V``  ``--version``    prints the version of Pyxel              optional
======  ===============  =======================================  ==========

..
    % Time dependent simulation and readout...
    For simulating the effects of different readout modes (like TDI or
    nondestructive Up-The-Ramp sampling) or time-dependent models (like
    persistence), the framework includes a time stepping loop, which can
    feed the pipeline repeatedly with the output Detector objects of the
    previous run. During each step, the time value is increased (according
    to the readout mode settings) and can be used by any time-dependent
    model in the inner pipeline. The time simulation of a Detector object
    is single-threaded, but more Detector objects can be simulated in
    parallel. After each time step, the current state of output Detector
    objects can be saved and used later, for example to plot parameters
    in function of time during post-processing.
    % Post-processing, outputs
    At the end of the simulation process, depending on the current running
    mode, the post-processing functions can extract data from a stack of
    output Detector objects and save them into output files. Various
    output types and formats are available for the users, such as
    images (FITS), plots (histograms, graphs), reports (jupyter
    notebook) and even the raw data (dataframes, arrays).


.. _single_mode:

Single mode
-------------

Running Pyxel in Single mode can be used to get a single image with
the detector effects defined in either the configuration file
or the GUI.

.. code-block:: yaml

  # YAML config file for Single mode

  simulation:
    mode: single


..
    either with or without a time dependent readout. In the former case,
    time evolution of images is available as well.


.. _parametric_mode:

Parametric mode
-----------------

The parametric mode of Pyxel can automatically change the value of any
detector or model parameter to make a sensitivity analysis for any parameter.

The variable parameter have to be defined in the YAML
configuration file with ranges or lists. The framework generates and runs
a stack of different Detector objects and pipelines.

At the end, the user can plot and analyze the data
in function of the variable parameter.

Sequential
***********

.. code-block:: yaml

  # YAML config file for Parametric mode (sequential)

  simulation:
    mode: parametric

    parametric:
      parametric_mode: sequential
      parameters:
        - key:      pipeline.charge_generation.tars.arguments.particle_number
          values:   [1, 2, 3]
          enabled:  true
        - key:      pipeline.photon_generation.illumination.arguments.level
          values:   range(0, 300, 100)
          enabled:  true

| The yaml file will start 6 runs in this order:
| number=1, number=2, number=3, level=0, level=100, level=200

The default values for 'number' and 'level' are defined as the arguments
of the specific models in the pipeline part of the yaml config file.

Embedded
***********

.. code-block:: yaml

  # YAML config file for Parametric mode (embedded)

  simulation:
    mode: parametric

    parametric:
      parametric_mode: embedded
      parameters:
        - key:      pipeline.charge_generation.tars.arguments.particle_number
          values:   [1, 2, 3]
          enabled:  true
        - key:      pipeline.photon_generation.illumination.arguments.level
          values:   range(0, 300, 100)
          enabled:  true

| The yaml file will start 9 runs in this order:
| (number=1, level=0), (number=1, level=100), (number=1, level=200),
| (number=2, level=0), (number=2, level=100), (number=2, level=200),
| (number=3, level=0), (number=3, level=100), (number=3, level=200)

The default values for 'number' and 'level' are defined as the arguments
of the specific models in the pipeline part of the yaml config file.

Parallel
*********

.. code-block:: yaml

  # YAML config file for Parametric mode (parallel)

  simulation:
    mode: parametric

    parametric:
      parametric_mode:  parallel
      from_file:        'outputs/calibration_champions.out'
      column_range:     [2, 17]
      parameters:
        - key:      detector.characteristics.amp
          values:   _
        - key:      pipeline.charge_transfer.cdm.arguments.tr_p
          values:   [_, _, _, _]
        - key:      pipeline.charge_transfer.cdm.arguments.nt_p
          values:   [_, _, _, _]
        - key:      pipeline.charge_transfer.cdm.arguments.sigma_p
          values:   [_, _, _, _]
        - key:      pipeline.charge_transfer.cdm.arguments.beta_p
          values:   _
        - key:      detector.environment.temperature
          values:   _

The parametric values (int, float or str) indicated with with '_' character,
and all are read and changed in parallel from an ASCII file defined
with ``from_file``.

Can be used for example to read output file of calibration running mode
containing the champion parameter set for each generation, and create one
output fits image for each generation to see the evolution.

.. _calibration_mode:

Calibration mode
------------------

The purpose of the Calibration mode is to find the optimal input arguments
of models or optimal detector attributes based on a
target dataset the models or detector behaviour shall reproduce.

..
    The architecture contains a data
    comparator function to compare simulated and measured data, then via a
    feedback loop, a function readjusts the model parameters (this function
    can be user defined).
    The Detection pipelines are re-run with the modified
    Detector objects. This iteration continues until reaching the convergence,
    i.e. we get a calibrated model fitted to the real, measured dataset.


.. code-block:: yaml

  # YAML config file for Calibration mode

  simulation:
    mode: calibration

    calibration:
      calibration_mode: pipeline                    # single_model

      output_type:      image                       # pixel # signal # image
      output_fit_range: [0, 20, 0, 30]

      target_data_path: [data/target.fits']         #  <*.npy> <*.fits> <ascii>
      target_fit_range: [10, 30, 20, 50]

      weighting_path:   ['data/weights.fits']

      fitness_function:
        func: pyxel.calibration.fitness.sum_of_abs_residuals
        arguments:

      algorithm:
        type:            sade                       # sga # nlopt
        generations:     20
        population_size: 100
        variant:         2

      seed:              1321

      parameters:
        - key:  detector.characteristics.amp
          values: _
          logarithmic: false
          boundaries: [1., 10.]
        - key:  pipeline.charge_transfer.cdm.arguments.tr_p
          values: [_, _, _, _]
          logarithmic: true
          boundaries: [1.e-3, 2.]
        - key:  pipeline.charge_transfer.cdm.arguments.nt_p
          values: [_, _, _, _]
          logarithmic: true
          boundaries: [1.e-2, 1.e+1]
        - key:  pipeline.charge_transfer.cdm.arguments.beta_p
          values: _
          logarithmic: false
          boundaries: [0., 1.]
