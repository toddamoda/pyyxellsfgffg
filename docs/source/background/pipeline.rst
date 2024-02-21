.. _pipeline:

########
Pipeline
########

The core algorithm of the architecture is the Detection pipeline allowing to
host any type of :ref:`models <models_explanation>` in a flexible manner, allowing for an arbitrary number of models.
It is an instance of :py:class:`~pyxel.pipelines.DetectionPipeline` class.

Inside the pipeline the :ref:`models <models_explanation>` are grouped into different
levels per detector type mirroring the operational principles of the detector, for example
in case of a :term:`CCD` the model groups are :ref:`scene generation <scene_generation>`,
:ref:`photon collection <photon_collection>`, :ref:`charge <charge_transfer>`, :ref:`generation <charge_generation>`,
:ref:`charge collection <charge_collection>`, :ref:`charge transfer <charge_transfer>`,
:ref:`charge measurement <charge_measurement>`, :ref:`readout electronics <readout_electronics>`
and :ref:`data processing <data_processing>` in this order.

Each group is structured around a for loop, iterating over all included and selected models in a predefined sequence,
which can be customized by the user. All models within a pipeline sequentially access and modify the same
:py:class:`~pyxel.detectors.Detector` object. pon completion, the pipeline yields the modified
:py:class:`~pyxel.detectors.Detector` object as output, ready for generating output files based on the results.

Since version 2.0, Pyxel possesses the ability to accommodate multiwavelength models.
These models, along with their associated groups, are visually highlighted by distinct colors in the accompanying image.
Integration of multiwavelength photons is conducted latest at the charge collection stage, ensuring their consolidation
across the designated wavelength range without delay.

.. image:: _static/pipeline.png
    :width: 600px
    :alt: ccd_pipeline
    :align: center

.. _models_explanation:

Models
======

When referring to "models," we are discussing various analytical functions, numerical methods, or algorithms designed
to approximate, calculate, and visualize electro-optical performance and degradation resulting from operational
environments such as space or laboratory tests, including their associated effects like radiation damage.

These models are Python functions that require a :py:class:`~pyxel.detectors.Detector` object as their input argument.
To incorporate a model, it must be added to the ``YAML`` configuration file. Subsequently, Pyxel automatically invokes the
function within a loop of its corresponding model group, passing the :py:class:`~pyxel.detectors.Detector` object to it.
The model function has the capability to modify this object, which is then utilized and further modified by subsequent
models in the pipeline.


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
    :width: 800px
    :alt: models
    :align: center

Most of the model groups work for :term:`CCD`, :term:`CMOS`, :term:`MKID` and :term:`APD` detectors,
which are imitating the physical working principles of imaging detectors. They were
grouped according to which physics data storing objects are modified by them. Note that among the 10 groups,
three are dedicated to a single detector type. They are visually highlighted in the accompanying image.

Model functions
---------------

A model function is a function that takes in the :py:class:`~pyxel.detectors.Detector` object as one of the arguments
and edits the data stored in it.
The :py:class:`~pyxel.detectors.Detector` object serves as the mandatory input argument,
and may vary in type, such as a :py:class:`~pyxel.detectors.CCD` or
a :py:class:`~pyxel.detectors.CMOS` type :py:class:`~pyxel.detectors.Detector` object,
depending on the simulation requirements of the model.
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

For more details, see the :ref:`adding new models <new_model>` page.
