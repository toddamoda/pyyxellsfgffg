.. _models:

======
Models
======

The containers such as :py:class:`~pyxel.data_structure.Scene`, :py:class:`~pyxel.data_structure.Photon`,
:py:class:`~pyxel.data_structure.Pixel`, :py:class:`~pyxel.data_structure.Signal` and
:py:class:`~pyxel.data_structure.Image` are not initialized before running a pipeline.
The models inside the model groups must initialize the containers.

.. deprecated:: 1.7

    The models groups **photon generation** and **optics** have been deprecated and
    will be removed for version 2.0.

    All models from **photon generation** and **optics** are moved to the new
    model group :ref:`photon collection <photon_collection>`.

    Example of migration from a model from 'Photon Generation' to 'Optics':

    Before:

    .. code-block:: yaml

        pipeline:
          photon_generation:
            - name: shot_noise
              func: pyxel.models.photon_generation.shot_noise
              enabled: true

          optics:
            - name: optical_psf
              func: pyxel.models.optics.optical_psf
              enabled: true
              arguments:
                fov_arcsec: 5 # FOV in arcseconds
                pixelscale: 0.01 #arcsec/pixel

    After:

    .. code-block:: yaml

        pipeline:
          photon_collection:
        # ^^^^^^^^^^^^^^^^^
        #      modified

            - name: shot_noise
              func: pyxel.models.photon_collection.shot_noise
            #       ~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^~~~~~~~~~~~
            #                         modified
              enabled: true

            - name: optical_psf
              func: pyxel.models.photon_collection.optical_psf
            #       ~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^~~~~~~~~~~~~
            #                         modified
              enabled: true
              arguments:
                fov_arcsec: 5 # FOV in arcseconds
                pixelscale: 0.01 #arcsec/pixel


.. toctree::

   model_groups/scene_generation_models.rst
   model_groups/photon_collection_models.rst
   model_groups/charge_generation_models.rst
   model_groups/charge_collection_models.rst
   model_groups/phasing_models.rst
   model_groups/charge_transfer_models.rst
   model_groups/charge_measurement_models.rst
   model_groups/readout_electronics.rst
   model_groups/data_processing_models.rst
