.. _new_model:

Adding new models
===================

:ref:`Models <models>`

Users and developers can easily add any kind of new or already existing
model to Pyxel, thanks to the model plug-in mechanism developed for this
purpose.


The YAML file
---------------

You need to add your model function to the :ref:`YAML config file <yaml>`,
providing the input arguments for the function.

You should copy the python file including your function in the folder
``pyxel/pyxel/models/<model_group>/``.

.. code-block:: yaml

  # YAML config file with a new model in photon_generation

  pipeline:
    class: pyxel.pipelines.ccd_pipeline.CCDDetectionPipeline

    photon_generation:
      - name: photon_level
        func: pyxel.models.photon_generation.add_photons.add_photons
        enabled: true
        arguments:
          level: 1000

      #######################################################################
      - name: my_model                                                      #
        func: pyxel.models.photon_generation.my_script.my_model_function    #
        enabled: true                                                       #
        arguments:                                                          #
          file: '/path/to/file.fits'                                        #
          arg:  124                                                         #
      #######################################################################

      - name: shot_noise
        func: pyxel.models.photon_generation.shot_noise.shot_noise
        enabled: false


Model wrapper
----------------

If your model is a Python class, package or it is implemented in a
programming language other than Python (C/C++, Fortran, Java),
then it is necessary to create a wrapper model function,
which calls and handles the code (class, package or
non-Python code).


Argument validation
---------------------

To validate input arguments of a model function, use the
``validate`` and ``argument`` Pyxel decorators:

.. code-block:: python

    import pyxel

    @pyxel.validate
    @pyxel.argument(name='file', label='a fits file', validate=check_path)
    @pyxel.argument(name='arg', label='an integer number', units='', validate=check_type(int))
    def my_model_function(detector: Detector, file: str, arg: int = 0):
        """This is my model with validated arguments.

        :param detector:
        :param file:
        :param arg:
        """
