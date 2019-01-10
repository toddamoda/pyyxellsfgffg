.. _running_modes:

Running Pyxel
==============


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
