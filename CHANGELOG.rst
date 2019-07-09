Changelog
=========


version 0.4 / 2019-07-09
------------------------

* Running modes implemented:
  * Calibration mode for model fitting and detector optimization
  * Dynamic mode for time-dependent (destructive and non-destructive) detector readout
  * Parallel option for Parametric mode
* Models added:
  * CDM Charge Transfer Inefficiency model
  * POPPY physical optical propagation model
  * SAR ADC signal digitization model
* Outputs class for post-processing and saving results
* Logging, setup and versioneer
* Examples
* Documentation

version 0.3 / 2018-03-26
------------------------

* Single and Parametric mode have been implemented
* Infrastructure code has been placed in 2 new projects: esapy_config and esapy_web
* Web interface (GUI) is dynamically generated based on attrs definitions
* NGHxRG noise generator model has been added

version 0.2 / 2018-01-18
------------------------

* TARS cosmic ray model has been reimplemented and added

version 0.1 / 2018-01-10
------------------------

* Prototype: first pipeline for a CCD detector