.. _running_modes:

Running Pyxel
==============


-c pyxel/io/config/input.yaml -o outputs/out.fits




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

Single mode is the simplest, it can be used to get a single image with
detector effects either with or without a time dependent readout. In the
former case, time evolution of images is available as well.


.. _parametric_mode:

Parametric analysis mode
--------------------------

The parametric mode of Pyxel can automatically change the value of any
detector or model parameter, which is an essential feature to make a
parameter sensitivity analysis. The variable parameter have to be defined
in advance in the YAML configuration file with ranges or lists. The
framework generates a stack of different Detector objects, then runs
separate identical pipelines in parallel (if more CPU threads are
available) with the different input Detectors. At the end, the user
can plot and analyze the data in function of the variable parameter.



.. _calibration_mode:

Calibration mode
------------------

The model calibration mode is a special case of the parametric mode,
with a purpose to find the optimal values of its parameters based on a
target dataset the model shall reproduce. The architecture contains a data
comparator function to compare simulated and measured data, then via a
feedback loop, a function readjusts the model parameters (this function
can be user defined). The Detection pipelines are re-run with the modified
Detector objects. This iteration continues until reaching the convergence,
i.e. we get a calibrated model fitted to the real, measured dataset.
