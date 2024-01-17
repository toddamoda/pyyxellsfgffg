.. _pipeline:

########
Pipeline
########

The core algorithm of the architecture is the Detection pipeline allowing to
host any type of :ref:`models <models_explanation>` in an arbitrary number.
It is an instance of :py:class:`~pyxel.pipelines.DetectionPipeline` class.

Inside the pipeline the :ref:`models <models_explanation>` are grouped into different
levels per detector type imitating the working principle of the detector, for example
in case of a :term:`CCD` the model groups are :ref:`scene generation <scene_generation>`,
:ref:`photon collection <photon_collection>`, :ref:`charge <charge_transfer>`, :ref:`generation <charge_generation>`,
:ref:`charge collection <charge_collection>`, :ref:`charge transfer <charge_transfer>`,
:ref:`charge measurement <charge_measurement>`, :ref:`readout electronics <readout_electronics>`
and :ref:`data processing <data_processing>` in this order.

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


Each group is based on a
for loop, looping over all the included and selected models in a predefined
order, which can be changed by the user. All the models in a pipeline, get
and modify the same :py:class:`~pyxel.detectors.Detector` object one after another.
At the end, the pipeline returns the :py:class:`~pyxel.detectors.Detector` object
as an output ready to generate output files from results.

.. image:: _static/pipeline.png
    :scale: 70%
    :alt: ccd_pipeline
    :align: center

.. _models_explanation:

Models
======

By models, we mean various analytical functions, numerical methods or
algorithms implemented in order to approximate, calculate, visualize
electro-optical performance and degradation due to the operational
environment (space, laboratory test) and its effects (e.g. radiation
damage).

Models are Python functions with a :py:class:`~pyxel.detectors.Detector` object
defined as their input argument. The model function has to be
added to the ``YAML`` configuration file.
Then the function is automatically called by Pyxel inside a loop of its
model group and the :py:class:`~pyxel.detectors.Detector` object is passed to it.
The model may modifies this :py:class:`~pyxel.detectors.Detector` object which is
also used and modified further by the next models in the pipeline.


.. _model_groups_explanation:

Model groups
------------

Models are grouped into multiple model groups per detector type according to
which object of the :py:class:`~pyxel.detectors.Detector` object is used or modified by
the models. These groups correspond roughly to the detector fundamental
functions.

Models in Pyxel makes changes and storing the data in data buckets (:py:class:`~pyxel.data_structure.Scene`,
:py:class:`~pyxel.data_structure.Photon`, :py:class:`~pyxel.data_structure.Charge`,
:py:class:`~pyxel.data_structure.Phase`,
:py:class:`~pyxel.data_structure.Pixel`, :py:class:`~pyxel.data_structure.Signal` or
:py:class:`~pyxel.data_structure.Image`,
:py:class:`datatree.DataTree` class).

Models could also modify any detector attributes (like Quantum Efficiency,
gains, temperature, etc.) stored in a Detector subclass
(:py:class:`~pyxel.detectors.Characteristics`, :py:class:`~pyxel.detectors.Environment`,
:py:class:`~pyxel.detectors.Material`).


Detector attributes changes could happen globally (on detector level)
or locally (on pixel level or only for a specific detector area).

.. figure:: _static/model-table.png
    :scale: 70%
    :alt: models
    :align: center

Most of the model groups work for :term:`CCD`, :term:`CMOS`, :term:`MKID` and :term:`APD` detectors,
which are imitating the physical working principles of imaging detectors. They were
grouped according to which physics data storing objects are modified by them. Note that 3 out of the 10 groups are
specific to a single detector type.

Model functions
---------------

A model function is a function that takes in the :py:class:`~pyxel.detectors.Detector` object as one of the arguments
and edits the data stored in it.
The :py:class:`~pyxel.detectors.Detector` object is the only compulsory input argument,
and can be of different types,  for example a :py:class:`~pyxel.detectors.CCD` or
a :py:class:`~pyxel.detectors.CMOS` type :py:class:`~pyxel.detectors.Detector` object,
depending on what the model is supposed to simulate.
Any other (optional) input arguments can be defined for the model as well,
which will be loaded from the :ref:`YAML <yaml>` file automatically.
Users can change model parameters or enable/disable them by interacting with the configuration file.
For example, a model function that multiplies the photon array with the input argument would look like this in the code:

.. code-block:: python

    from pyxel.detectors import Detector


    def my_model_function(detector: Detector, arg: int = 0):
        """This is my model that will multiply pixel array with the argument.

        Parameters
        ----------
        detector
        arg
        """
        detector.photon.array = detector.photon.array * arg
        return None


Adding a new model
------------------

Users and developers can easily add any kind of new or already existing
model to Pyxel, thanks to the easy-to-use model plug-in mechanism
developed for this purpose.

For more details, see the :ref:`Adding new models <new_model>` page.
