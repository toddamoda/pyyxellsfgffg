Pyxel development plans
==============================

Features
-------------

* Dynamic mode `ongoing`
  * clocking, time dependant (destructive and non-destructive) CMOS readout
  * time dependant modelling, global time increases each cycle, models depend on global time
* Material properties, compound materials
* Units, global constants
  * Astropy units
* Parallelisation: 
  * Multi-threading, multi-processing
    * Pygmo archpelago, islands: https://esa.github.io/pagmo2/
    * Dask: https://dask.org/
  * Submitting jobs to a GRID via Pyxel
    * Gripmap: https://gridmap.readthedocs.io/en/latest/
* Sensor geometry 
  * masking, roi, CCD pre- and over-scan regions, etc. 
* Outputs `ongoing`

Models
---------

* New models:
  * HxRG models: SAR ADC, Full Well, Dark current, noises - by Benoit Serra  `ongoing`
  * CERN Allpix-Squared framework to simulate charge diffusion
  * GalSim to generate images of astronomical objects (low priority)
  * Simple models: general CCD charge transfer model, Full Well, Non-linearity, PRNU, Photoelectric, Diffusion, Charge Injection, RTG, SEE, ADC, Quantization, Electric fields inside pixels, crosstalk

* CTI models:
  * Add ARCTIC CTI model
  * (Implement CDM in C to run it faster)
  
* Cosmic ray model: `ongoing`
  * Finish implementation and validation of TARS
  * Using TARS and/or Geant4 for PLATO irradiation proton spectra analysis
  * Using TARS for simulating and optimizing MCT detectors

User Interfaces
------------------

* Design and implement a Terminal User Interface (low priority)
* Design and implement a Graphical User Interface with Hans Smit (low priority)

Beta testing 
--------------

* Beta testing by internal and external users (in parallel with other activities)
* 2019 August: Finish and Deploy version 1.0 including all the feedback

Documentation
--------------
https://esa.gitlab.io/pyxel/doc/
Contribution guideline

Validation
----------------

Pyxel collaboration
--------------------- 

* IPR, licensing, going fully open-sourcing via GitLab
* critical mass of users
* new developers 
* monthly developer meetings (online) `started`
* forum
* mailing list
* webpage: http://sci.esa.int/pyxel
* Pyxel workshop

Others
-------

* Cleanup GitLab repo
