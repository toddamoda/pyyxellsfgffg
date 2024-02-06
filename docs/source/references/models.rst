.. _models:

======
Models
======

The containers such as :py:class:`~pyxel.data_structure.Scene`, :py:class:`~pyxel.data_structure.Photon`,
:py:class:`~pyxel.data_structure.Pixel`, :py:class:`~pyxel.data_structure.Signal` and
:py:class:`~pyxel.data_structure.Image` are not initialized before running a pipeline.
The models inside the model groups must initialize the containers.

* :ref:`scene_generation`
* :ref:`photon_collection`
* :ref:`charge_generation`
* :ref:`charge_collection`
* :ref:`phasing`
* :ref:`charge_transfer`
* :ref:`charge_measurement`
* :ref:`readout_electronics`
* :ref:`data_processing`

.. toctree::
   :caption: Model groups
   :maxdepth: 1
   :hidden:

   model_groups/scene_generation_models.rst
   model_groups/photon_collection_models.rst
   model_groups/charge_generation_models.rst
   model_groups/charge_collection_models.rst
   model_groups/phasing_models.rst
   model_groups/charge_transfer_models.rst
   model_groups/charge_measurement_models.rst
   model_groups/readout_electronics.rst
   model_groups/data_processing_models.rst
