.. _pipelines:

Pipelines
===========

Pipeline classes and their methods.


%pipeline
The core algorithm of the architecture is the Detection pipeline allowing to
host any type of models in an arbitrary number. This is either a CCD or a
CMOS Detection pipeline inheriting relevant subclasses, properties, functions
from a general Detection pipeline class.

Inside the pipeline the models are grouped into 7 different levels per
detector type imitating the working principle of the detector, for example
in case of a CCD the model levels are photon generation, optics, charge
generation, charge collection, charge transfer, charge measurement and
readout electronics. Each level is based on a
for loop, looping over all the included and selected models in a predefined
order, which can be changed by the user. All the models in a thread, get
and modify the same Detector object one after another. At the end, the
pipeline returns the Detector object as an output.


.. _ccd_pipeline:

CCD Pipeline
--------------

.. autoclass:: pyxel.pipelines.ccd_pipeline.CCDDetectionPipeline
    :members:
    :inherited-members:
    :undoc-members:
    :show-inheritance:
    :exclude-members:




.. _cmos_pipeline:

CMOS Pipeline
--------------

.. autoclass:: pyxel.pipelines.cmos_pipeline.CMOSDetectionPipeline
    :members:
    :inherited-members:
    :undoc-members:
    :show-inheritance:
    :exclude-members:
