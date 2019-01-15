.. _models:

Models
===========

By models, we mean various analytical functions, numerical methods or
algorithms implemented in order to approximate, calculate, visualize
electro-optical performance and degradation due to the operational
environment (space, laboratory test) and its effects (e.g. radiation
damage).

Models are Python functions with a Detector object defined as
their input argument. The model function has to be
registered in Pyxel model registry and added to the YAML configuration file.
Then the function is automatically called by Pyxel inside a loop of its
model group (level) and the Detector object is passed to it. The model modifies
this Detector object which is also used and modified further by the next
models in the pipeline.


**Model groups**

    Models are grouped into 7 model levels per detector type according to
    which object of the Detector object is used or modified by
    the models. These levels correspond roughly to the detector fundamental
    functions.

    Models in Pyxel makes changes and storing there data in data structure
    classes (Photon, Charge, Pixel, Signal or Image class).
    For details, see the :ref:`Data Structure <data_structure>` page.

    Models could also modify any detector attributes (like Quantum Efficiency,
    gains, temperature, etc.) stored in a Detector subclass (Characteristics,
    Environment, Material).

..
    Detector attributes changes could happen globally (on detector level)
    or locally (on pixel level or only for a specific detector area).

.. figure:: _static/model-table.PNG
    :scale: 70%
    :alt: models
    :align: center

    All the 8 model levels, which are imitating the physical working principles of imaging detectors. They were
    grouped according to which physics data storing objects are modified by them. Note that 2 out of the 8 levels are
    specific to a single detector type.


**Model inputs**

    Models functions have at least one compulsory input argument,
    which is either a general, a CCD or a CMOS type Detector object,
    depending on what the model is supposed to simulate:
    a general (e.g. cosmic rays),
    a CCD (e.g. CTI) or a CMOS (e.g. Alternating Column Noise) specific
    detector effect.

    Any other (optional) input arguments can be defined for the model as well,
    which will be loaded from the YAML file or GUI and passed to the model
    automatically.

**Adding new models**

    Users and developers can easily add any kind of new or already existing
    model to Pyxel, thanks to the easy-to-use model plug-in mechanism
    developed for this purpose.

    For more details, see the :ref:`Adding new models <new_model>` page.

.. _photon_generation:

Photon Generation models
---------------------------------

.. automodule:: pyxel.models.photon_generation
    :members:
    :undoc-members:
    :imported-members:

Simple photon generation
***************************

.. autofunction:: pyxel.models.photon_generation.add_photons.add_photons(param1 = None, param2)

Loading image
***************************

.. autofunction:: pyxel.models.photon_generation.load_image.load_image(param1, param2: int = 0)

Shot noise
***************************

.. autofunction:: pyxel.models.photon_generation.shot_noise.add_shot_noise(param1, param2)


.. _optical:

Optical models
---------------------------------

.. automodule:: pyxel.models.optics
    :members:
    :undoc-members:
    :imported-members:


.. _charge_generation:

Charge Generation models
---------------------------------

.. automodule:: pyxel.models.charge_generation
    :members:
    :undoc-members:
    :imported-members:

Simple photoconversion
***************************

.. autofunction:: pyxel.models.charge_generation.photoelectrons.simple_conversion


TARS cosmic ray model
***************************

A cosmic ray event simulator was the first model added to Pyxel.
Initially it was a simple, semi-analytical model in Fortran using the stopping
power curve of protons to optimize the on-board source detection algorithm
of the Gaia telescope to discriminate between stars and cosmic rays. Then it
was reimplemented in Python as TARS (Tools for Astronomical Radiation
Simulations).

It is now being upgraded to either randomly sample distributions pre-generated
using Geant4 Monte Carlo particle transport simulations or directly call a
Geant4 application for each single event. The validation of the latest
version of the model against cosmic ray signals of the Gaia Basic Angle
Monitor CCDs is ongoing via Pyxel.

.. autofunction:: pyxel.models.charge_generation.tars.tars.run_tars


CCD charge injection
***************************

.. autofunction:: pyxel.models.charge_generation.charge_injection.charge_injection


.. _charge_collection:

Charge Collection models
---------------------------------

.. automodule:: pyxel.models.charge_collection
    :members:
    :undoc-members:
    :imported-members:

Simple charge collection
***************************

.. autofunction:: pyxel.models.charge_collection.collection.simple_collection

Fix pattern noise
***************************

.. autofunction:: pyxel.models.charge_collection.fix_pattern_noise.add_fix_pattern_noise

Simple full well
***************************

.. autofunction:: pyxel.models.charge_collection.full_well.simple_pixel_full_well


.. _charge_transfer:

Charge Transfer models (CCD)
---------------------------------

.. important::
    Only for CCD detectors!

.. automodule:: pyxel.models.charge_transfer
    :members:
    :undoc-members:
    :imported-members:

Charge Distortion Model (CDM)
*******************************

The Charge Distortion Model (CDM) describes the effects of the radiation
damage causing charge deferral and image shape distortion. The analytical
model is physically realistic, yet fast enough. It was developed specifically
for the Gaia CCD operating mode, implemented in Fortran and Python. However,
a generalized version has already been applied in a broader context, for
example to investigate the impact of radiation damage on the Euclid mission.
This generalized version has been included and used in Pyxel.

.. autofunction:: pyxel.models.charge_transfer.cdm.CDM.cdm


.. _charge_measurement:

Charge Measurement models
---------------------------------

.. automodule:: pyxel.models.charge_measurement
    :members:
    :undoc-members:
    :imported-members:

Simple charge measurement
*******************************

.. autofunction:: pyxel.models.charge_measurement.measurement.simple_measurement

Output node noise
*******************************

.. autofunction:: pyxel.models.charge_measurement.readout_noise.output_node_noise


.. _signal_transfer:

Signal Transfer models (CMOS)
---------------------------------

.. important::
    Only for CMOS-based detectors!

.. automodule:: pyxel.models.signal_transfer
    :members:
    :undoc-members:
    :imported-members:

HxRG noise generator
*******************************

A near-infrared CMOS noise generator (ngHxRG) developed for the
James Webb Space Telescope (JWST) Near Infrared Spectrograph (NIRSpec)
has been also added to the framework. It simulates many important noise
components including white read noise, residual bias drifts, pink 1/f
noise, alternating column noise and picture frame noise.

This model implemented in Python, reproduces most of the Fourier noise
power spectrum seen in real data, and includes uncorrelated, correlated,
stationary and non-stationary noise components.
The model can simulate noise for HxRG detectors of
Teledyne Imaging Sensors with and without the SIDECAR ASIC IR array
controller.

**kTC bias noise**

.. autofunction:: pyxel.models.signal_transfer.nghxrg.nghxrg.ktc_bias_noise

**White readout noise**

.. autofunction:: pyxel.models.signal_transfer.nghxrg.nghxrg.white_read_noise

**Alternating column noise (ACN)**

.. autofunction:: pyxel.models.signal_transfer.nghxrg.nghxrg.acn_noise

**Uncorrelated pink noise**

.. autofunction:: pyxel.models.signal_transfer.nghxrg.nghxrg.uncorr_pink_noise

**Correlated pink noise**

.. autofunction:: pyxel.models.signal_transfer.nghxrg.nghxrg.corr_pink_noise

**PCA0 noise**

.. autofunction:: pyxel.models.signal_transfer.nghxrg.nghxrg.pca_zero_noise


.. _readout_electronics:

Readout Electronics models
---------------------------------

.. automodule:: pyxel.models.readout_electronics
    :members:
    :undoc-members:
    :imported-members:

Simple digitization
*******************************

.. autofunction:: pyxel.models.readout_electronics.digitization.simple_digitization
