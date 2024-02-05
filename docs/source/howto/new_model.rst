.. _new_model:

=================
Adding new models
=================

Users and developers can easily add any kind of new or already existing
model to Pyxel, thanks to the model plug-in mechanism developed for this
purpose.

Existing models: :ref:`Models <models>`


Model function
==============

A model function is a function that takes in the :py:class:`~pyxel.detectors.Detector` object as one of the arguments
and edits the data stored in it. To add it to Pyxel, you have to copy the script containing your function,
let's say ``my_script.py``, into the corresponding model group folder in Pyxel.
For example if our function edits the photon array, the script ``my_script.py`` should go into ``pyxel/models/photon_collection``.
A model function that multiplies the photon array with the input argument would look like this:

.. code-block:: python

    from pyxel.detectors import Detector


    def my_model_function(detector: Detector, arg: int = 0) -> None:
        """This is my model that will multiply pixel array with the argument.

        Parameters
        ----------
        detector
        arg
        """
        detector.photon.array = detector.photon.array * arg
        return None

Editing the YAML file
=====================

To use the new model function in a Pyxel pipeline
you need to add your model function to the :ref:`YAML config file <yaml>`,
providing the input arguments for the function.

.. code-block:: yaml

  # YAML config file with a new model in photon_collection

  pipeline:

    photon_collection:
      - name: some_other_model
        func: pyxel.models.photon_collection.some_other_model
        enabled: true
        arguments:
          wavelength: 650
          NA: 0.9

      #######################################################################
      - name: my_model                                                      #
        func: pyxel.models.photon_collection.my_script.my_model_function    #
        enabled: true                                                       #
        arguments:                                                          #
          arg:  124                                                         #
      #######################################################################


.. tip::
    If we import ``my_model_function`` in the ``pyxel/models/photon_collection/__init__.py``,
    then the path to the model is shorter: ``func: pyxel.models.photon_collection.my_model_function``.


Model wrapper
=============

If your model is a Python class, package or it is implemented in a
programming language other than Python (C/C++, Fortran, Java),
then it is necessary to create a wrapper model function,
which calls and handles the code (class, package or
non-Python code).

Creating a new model with a Pyxel command
=========================================

It is possible to create a new model from an already prepared template with the built in command like so:

.. code-block:: bash

    pyxel create-model photon_collection/new_model

    or

    python -m pyxel create-model photon_collection/new_model

This will create a new python script ``new_model.py`` with a template model function
in folder ``pyxel/models/photon_collection``. All you have to do is edit your model function
and the docstring and then copy the ``YAML`` configuration section from the docstring into the desired configuration file.
Don't forget to import your model function in the ``__init__.py`` file of the appropriate model group for faster access.

Best Practices
==============

Write models as pairs of pure and impure functions
--------------------------------------------------

If a model is changing one of the data structures stored in the :py:class:`~pyxel.detectors.Detector` object,
then it is advised to write the model as a pair of functions:
one as an impure function that changes the state of the :py:class:`~pyxel.detectors.Detector` object;
the other as a pure function that does the actual calculations without changing the state of the input arguments.

More info on pure and impure functions: https://en.wikipedia.org/wiki/Pure_function,
https://alvinalexander.com/scala/fp-book/benefits-of-pure-functions/.

So instead of this:

.. code-block:: python

    # impure function
    def my_model(detector: Detector, arg: int) -> None:
        input_array = detector.pixel.array
        # do computations with array
        output_array = arg * input_array

        detector.pixel.array = output_array


Do this:

.. code-block:: python

    # pure function
    def compute_model_effect(input_array: numpy.ndarray, arg: int) -> np.ndarray:
        # do computations with array
        output_array = arg * input_array

        return output_array


    # impure function
    def my_model(detector: Detector, arg: int) -> None:
        input_array = detector.pixel.array  # type: np.ndarray

        output_array = compute_model_effect(input_array=input_array, arg=arg)

        detector.pixel.array = output_array

This way the model effect and the function ``compute_model_effect`` are much easier to test,
also it simplifies the use of package ``numba`` for speeding up code.


Using the numpy.random module in models
---------------------------------------

If a model uses functions from ``numpy.random`` module,
avoid resetting the global seed with ``numpy.random.seed()`` inside the model,
instead use the "with" statement function ``set_random_seed`` from ``pyxel.util``
and provide an optional argument ``seed``.
The function ``set_random_seed`` will use this seed to temporary change the state of the random generator,
or keep the same state (use the outer scope seed) if no specific seed is provided.

Example:

.. code-block:: python

    from pyxel.util import set_random_seed


    def my_model(detector, user_arg, seed=None):
        input_array = detector.pixel.array

        with set_random_seed(seed):
            # compute_model_effect uses functions from numpy.random module
            output_array = compute_model_effect(input_array=input_array, arg=arg)

        detector.pixel.array = output_array
