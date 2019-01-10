.. _yaml:

Configuration files
====================

The framework uses a user-friendly, structured YAML configuration file as an
input, which defines all the detector parameters, detector effect models and
their input arguments.

After the framework loads and
validates the YAML file (with .yaml extension),
then it creates *Detector* and *Detection Pipeline* object(s) based on
the YAML file with all the information needed for the framework to run
the simulation.

.. figure:: _static/yaml_new.png
    :alt: yaml
    :align: center

    The structured YAML configuration file of Pyxel.
    Left: Parts of the file where the running mode and detector parameters are defined;
    Right: Some model levels with all the models and their arguments inside.

The YAML configuration file of Pyxel is structured
similarly to the architecture, so the Pyxel class hierarchy can be
recognized in the group hierarchy of YAML files.

The groups and subgroups of the YAML file create objects from the
classes defined with their *class* arguments. During this process,
classes get all the parameters as input arguments defined within the group
or subgroup.

* **simulation:**

    In the beginning of the configuration file, the user should define
    the running mode. For details, see :ref:`running_modes`.

* **detector:**

    All arguments of Detector subclasses (Geometry, Characteristics,
    Environment, Material and Optics) are defined here.
    For details, see :ref:`detectors`.

* **pipeline:**

    It contains the model levels as subgroups
    (*photon_generation*, *optics*, *charge_generation*, etc.).
    For details, see :ref:`pipelines`.

    The order of model levels and models are important,
    as the execution order is defined here!

    * **photon_generation**
    * **optics**
    * **charge_generation**
    * **charge_collection**
    * **(charge_transfer)**
    * **charge_measurement**
    * **(signal_transfer)**
    * **readout_electronics**


    Models need a *name* which defines the path to the model wrapper
    function. Models also have an *enabled* boolean switch, where the user
    can enable or disable the given model. The optional and compulsory
    arguments of the model functions have to be listed inside the
    *arguments*. For details, see :ref:`models`.


Argument validation
-------------------

Independently of which UI is used to run the framework, before starting
the simulation, Pyxel validates all input arguments using the
Attrs Python package via esapy-config.

Usually it validates the type and range of parameters, attributes
when a validation rule is defined.

These validation rules could be also defined for
any model input arguments via a simple Python decorator.
