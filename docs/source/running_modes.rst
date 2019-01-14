.. _running_modes:

Running Pyxel
==============

To run Pyxel on your local computer, simply run it from the command-line:

.. code-block:: bash

  python pyxel/run.py
         -c pyxel/io/config/input.yaml
         -o outputs/out.fits

where

======  ===============  =======================================  ==========
``-c``  ``--config``     defines the path of the input YAML file  compulsory
``-o``  ``--output``     defines the path of the output file(s)   optional
``-s``  ``--seed``       defines a seed for random number         optional
                         generator
``-g``  ``--gui``        runs the Graphical User Interface (GUI)  optional
``-p``  ``--port``       defines a port to run the web            optional
                         server and GUI
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


.. code-block:: yaml

  # YAML config file for Parametric mode

  simulation:
    mode: parametric

    parametric:
      parametric_mode: sequential           # embedded # image_generator
      steps:
        -
          enabled: true
          key: pipeline.charge_generation.tars.arguments.particle_number
          values: [1, 2, 3]
        -
          enabled: true
          key: pipeline.photon_generation.photon_level.arguments.level
          values: range(100, 200, 10)


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
      calibration_mode: single_model                # pipeline

      output_type:      pixel                       # signal # image
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

      model_names:         ['cdm']
      variables:           [['tr_p', 'nt_p', 'sigma_p', 'beta_p']]
      params_per_variable: [[4, 4, 4, 1]]
      var_log:             [[True, True, True, False]]
      lower_boundary:      [[1.e-3, 1.e-2, 1.e-20, 0.]]
      upper_boundary:      [[2., 1.e+1, 1.e-15, 1.]]
