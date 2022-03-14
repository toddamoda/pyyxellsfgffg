=========
Changelog
=========


UNRELEASED
==========

Core
----
* Remove maximum limit for attributes 'col' and 'row' in class ``Geometry``.
  The previous limit was set at a maximum of 10000 columns and 10000 rows.
  (See `!434 <https://gitlab.com/esa/pyxel/-/merge_requests/434>`_).

Documentation
-------------

Models
------

Others
------
* Updated ``poppy`` dependency to version 1.0.2. The previous version of ``poppy``
  are not compatible with ``astropy`` version 5.0.1.
  (See `!431 <https://gitlab.com/esa/pyxel/-/merge_requests/431>`_).
* Fix an issue when building the documentation with Python 3.8.
  (See `!436 <https://gitlab.com/esa/pyxel/-/merge_requests/436>`_).


version 1.0.0 / 2022-02-10
==========================

We are happy to announce that Pyxel has reached a stable version 1.0.0!
Pyxel releases will use `semantic versioning <https://semver.org/>`_ notation.
Version 1.0 brings a simplified user experience, new models, 
parallel computing in observation mode, updated documentation, 
new examples, various bug fixes and much more. 
Excited for what comes next, stay tuned!

**Changes since last version:**

Documentation
-------------
* Add pyxel brief history to documentation.
  (See `!429 <https://gitlab.com/esa/pyxel/-/merge_requests/429>`_).


version 1.0.0-rc.6 / 2022-02-09
===============================

Others
------
* Update function display_persist.
  (See `!426 <https://gitlab.com/esa/pyxel/-/merge_requests/426>`_).


version 1.0.0-rc.5 / 2022-02-09
===============================

Others
------
* Implement option to save outputs in common picture formats.
  (See `!416 <https://gitlab.com/esa/pyxel/-/merge_requests/416>`_).
* Update MANIFEST.in.
  (See `!423 <https://gitlab.com/esa/pyxel/-/merge_requests/423>`_).


version 1.0.0-rc.4 / 2022-01-27
===============================

Models
------
* Fix a bug when converting to photons in load_image.
  (See `!419 <https://gitlab.com/esa/pyxel/-/merge_requests/419>`_).

Others
------
* Pin astropy version due to a bug.
  (See `!420 <https://gitlab.com/esa/pyxel/-/merge_requests/420>`_).


version 1.0.0-rc.3 / 2022-01-26
===============================

Core
----
* Improve digitization models and detector digitization characteristics.
  (See `!413 <https://gitlab.com/esa/pyxel/-/merge_requests/413>`_).
* Remove default values from detector properties.
  (See `!415 <https://gitlab.com/esa/pyxel/-/merge_requests/415>`_).

Documentation
-------------
* Put labels to model API to know which data structures are models changing.
  (See `!405 <https://gitlab.com/esa/pyxel/-/merge_requests/405>`_).
* Improved acronyms.
  (See `!414 <https://gitlab.com/esa/pyxel/-/merge_requests/414>`_).

Models
------
* Nghxrg model replacing pixel array instead of adding.
  (See `!404 <https://gitlab.com/esa/pyxel/-/merge_requests/404>`_).
* Optimize persistence model.
  (See `!285 <https://gitlab.com/esa/pyxel/-/merge_requests/285>`_).
* Fix for persistence model when using long time steps.
  (See `!407 <https://gitlab.com/esa/pyxel/-/merge_requests/407>`_).
* Rename TARS to Cosmix.
  (See `!409 <https://gitlab.com/esa/pyxel/-/merge_requests/409>`_).
* Add a simple ADC model.
  (See `!410 <https://gitlab.com/esa/pyxel/-/merge_requests/410>`_).

Others
------
* Fix mypy issues with new version of numpy 1.22.0.
  (See `!408 <https://gitlab.com/esa/pyxel/-/merge_requests/408>`_).


version 1.0.0-rc.2 / 2022-01-18
===============================

Core
----
* Fix Characteristics validation checks.
  (See `!402 <https://gitlab.com/esa/pyxel/-/merge_requests/402>`_).


version 1.0.0-rc.1 / 2022-01-18
===============================

Core
----

* Rename detector properties using whole words.
  (See `!292 <https://gitlab.com/esa/pyxel/-/merge_requests/292>`_).
* Review classes Material and Environment.
  (See `!393 <https://gitlab.com/esa/pyxel/-/merge_requests/393>`_).

Documentation
-------------

* Add more documentation for CCDCharacteristics, CMOSCharacteristics, ....
  (See `!399 <https://gitlab.com/esa/pyxel/-/merge_requests/399>`_).

Others
------

* Small simplification. From `Albern S. <https://gitlab.com/abnsy>`.
  (See `!395 <https://gitlab.com/esa/pyxel/-/merge_requests/395>`_).
* Updated ESA Copyright to 2022.
  (See `!396 <https://gitlab.com/esa/pyxel/-/merge_requests/396>`_).
* Fix issue with licenses.
  (See `!397 <https://gitlab.com/esa/pyxel/-/merge_requests/397>`_).
* Remove dead code.
  (See `!398 <https://gitlab.com/esa/pyxel/-/merge_requests/398>`_).


version 0.11.7 / 2022-01-07
===========================

Documentation
-------------

* Fix broken links in the documentation.
  (See `!388 <https://gitlab.com/esa/pyxel/-/merge_requests/388>`_).
* Fix links for 'suggest_edit' button in the documentation.
  (See `!389 <https://gitlab.com/esa/pyxel/-/merge_requests/389>`_).
* Add better documentation for running modes..
  (See `!390 <https://gitlab.com/esa/pyxel/-/merge_requests/390>`_).

Models
------

* Refactoring of CDM model.
  (See `!375 <https://gitlab.com/esa/pyxel/-/merge_requests/375>`_).

Others
------

* Add netcdf4 to function show_versions.
  (See `!383 <https://gitlab.com/esa/pyxel/-/merge_requests/383>`_).
* Fix issue with script 'download_last_environment_artifact.py'.
  (See `!386 <https://gitlab.com/esa/pyxel/-/merge_requests/386>`_).


version 0.11.6 / 2021-12-13
===========================

Core
----

* Add new attribute 'Config.detector'.
  (See `!378 <https://gitlab.com/esa/pyxel/-/merge_requests/378>`_).


Documentation
-------------

* Split documentation into 'stable' and 'latest''.
  (See `!380 <https://gitlab.com/esa/pyxel/-/merge_requests/380>`_).

Others
------

* Include netcdf4 in dependencies.
  (See `!374 <https://gitlab.com/esa/pyxel/-/merge_requests/374>`_).


version 0.11.5 / 2021-12-07
===========================

Core
----

* Fix an issue with calibration.
  (See `!353 <https://gitlab.com/esa/pyxel/-/merge_requests/353>`_).
* Use an array in 'Charge' besides a dataframe.
  (See `!351 <https://gitlab.com/esa/pyxel/-/merge_requests/351>`_).
* Move some general processing function into a common folder.
  (See `!359 <https://gitlab.com/esa/pyxel/-/merge_requests/359>`_).
* Use detector.time_step in charge_generation models and allow floats in Charge arrays.
  (See `!365 <https://gitlab.com/esa/pyxel/-/merge_requests/365>`_).

Models
------

* Model 'nghxrg' is not working on Windows.
  (See `!361 <https://gitlab.com/esa/pyxel/-/merge_requests/361>`_).
* Remove alignment model.
  (See `!364 <https://gitlab.com/esa/pyxel/-/merge_requests/364>`_).
* Implement a non-linear FWC.
  (See `!338 <https://gitlab.com/esa/pyxel/-/merge_requests/338>`_).
* Create a dark current model.
  (See `!310 <https://gitlab.com/esa/pyxel/-/merge_requests/310>`_).


version 0.11.4 / 2021-11-23
===========================

Core
----

* Implement array-like data structures as numpy custom array containers.
  (See `!325 <https://gitlab.com/esa/pyxel/-/merge_requests/325>`_).

Documentation
-------------

* Add more internal links in the documentation.
  (See `!333 <https://gitlab.com/esa/pyxel/-/merge_requests/333>`_).
* Move 'optical_psf' documentation to RST file.
  (See `!343 <https://gitlab.com/esa/pyxel/-/merge_requests/343>`_).

Models
------

* Move some models from 'readout_electronics' into separated files.
  (See `!323 <https://gitlab.com/esa/pyxel/-/merge_requests/323>`_).
* Display model's name when running a pipeline.
  (See `!335 <https://gitlab.com/esa/pyxel/-/merge_requests/335>`_).
* Add option to enable or disable progress bar in TARS model.
  (See `!337 <https://gitlab.com/esa/pyxel/-/merge_requests/337>`_).

Others
------

* Use 'deployment' in CI/CD.
  (See `!336 <https://gitlab.com/esa/pyxel/-/merge_requests/336>`_).
* Fix an issue in CI/CD.
  (See `!340 <https://gitlab.com/esa/pyxel/-/merge_requests/340>`_).
* Swap the environments name 'production' and 'development'.
  (See `!342 <https://gitlab.com/esa/pyxel/-/merge_requests/342>`_).


version 0.11.3 / 2021-11-15
===========================

Core
----

* Multiply photon flux with detector time step in photon generation models.
  (See `!305 <https://gitlab.com/esa/pyxel/-/merge_requests/305>`_).
* Initialize Photon class in detector reset function instead in models.
  (See `!309 <https://gitlab.com/esa/pyxel/-/merge_requests/309>`_).
* Resolve "Use a 'with' statement to set a seed with 'numpy.random'.
  (See `!175 <https://gitlab.com/esa/pyxel/-/merge_requests/175>`_).

Others
------

* Remove some TODOs.
  (See `!288 <https://gitlab.com/esa/pyxel/-/merge_requests/288>`_).


version 0.11.2 / 2021-11-09
===========================

Core
----

* Remove unnecessary warnings when Pygmo is not installed.
  (See `!286 <https://gitlab.com/esa/pyxel/-/merge_requests/286>`_).
* Remove parallel computing with Numba.
  (See `!290 <https://gitlab.com/esa/pyxel/-/merge_requests/290>`_).
* Use library 'click' to generate a Command Line Interface for script 'pyxel/run.py'.
  (See `!287 <https://gitlab.com/esa/pyxel/-/merge_requests/287>`_).
* Simplify imports of sub packages.
  (See `!296 <https://gitlab.com/esa/pyxel/-/merge_requests/296>`_).
* Fix an issue in imports.
  (See `!297 <https://gitlab.com/esa/pyxel/-/merge_requests/297>`_).
* Re-enable dask for observation mode.
  (See `!172 <https://gitlab.com/esa/pyxel/-/merge_requests/172>`_).

Documentation
-------------

* Make pyxel compatible with Python 3.9.
  (See `!289 <https://gitlab.com/esa/pyxel/-/merge_requests/289>`_).
* Update adding new models documentation with best practices.
  (See `!293 <https://gitlab.com/esa/pyxel/-/merge_requests/293>`_).
* Add a 'Asking for help' chapter in the documentation.
  (See `!299 <https://gitlab.com/esa/pyxel/-/merge_requests/299>`_).

Others
------

* Fix issue with xarray 0.20.
  (See `!291 <https://gitlab.com/esa/pyxel/-/merge_requests/291>`_).
* Updated black, isort and blackdoc in '.pre-commit.yaml'.
  (See `!294 <https://gitlab.com/esa/pyxel/-/merge_requests/294>`_).
* Partially reduce Pyxel start-up time.
  (See `!302 <https://gitlab.com/esa/pyxel/-/merge_requests/302>`_).


version 0.11.1 / 2021-10-29
===========================

Models
------

* Add a readout noise model for CMOS detectors.
  (See `!283 <https://gitlab.com/esa/pyxel/-/merge_requests/283>`_).


version 0.11 / 2021-10-27
=========================

Core
----

* Output folder already existing when running 'load' two times.
  (See `!232 <https://gitlab.com/esa/pyxel/-/merge_requests/232>`_).
* Implement normalisation for calibration mode.
  (See `!266 <https://gitlab.com/esa/pyxel/-/merge_requests/266>`_).
* Refactor class `Charge`.
  (See `!271 <https://gitlab.com/esa/pyxel/-/merge_requests/271>`_).
* Add new detector MKID. `Enrico Biancalani <https://gitlab.com/Dr_Bombero>`
  (See `!206 <https://gitlab.com/esa/pyxel/-/merge_requests/206>`_).
* Refactor single and dynamic mode into one named observation.
  (See `!263 <https://gitlab.com/esa/pyxel/-/merge_requests/263>`_).
* Include observation mode functions in parametric mode.
  (See `!264 <https://gitlab.com/esa/pyxel/-/merge_requests/264>`_).
* Include observation mode functions in calibration mode.
  (See `!265 <https://gitlab.com/esa/pyxel/-/merge_requests/265>`_).
* Rename observation to exposure and parametric to observation.
  (See `!274 <https://gitlab.com/esa/pyxel/-/merge_requests/274>`_).
* Improve the speed of function detector.reset.
  (See `!273 <https://gitlab.com/esa/pyxel/-/merge_requests/273>`_).
* Optimize the speed of calibration in time-domain.
  (See `!276 <https://gitlab.com/esa/pyxel/-/merge_requests/276>`_).

Documentation
-------------

* Add more information about how-to release to Conda Forge.
  (See `!252 <https://gitlab.com/esa/pyxel/-/merge_requests/252>`_).
* Update documentation on the refactored running modes.
  (See `!277 <https://gitlab.com/esa/pyxel/-/merge_requests/277>`_).
* Update installation instructions for using pip and conda.
  (See `!279 <https://gitlab.com/esa/pyxel/-/merge_requests/279>`_).
* Fix typos in installation instructions in documentation.
  (See `!280 <https://gitlab.com/esa/pyxel/-/merge_requests/280>`_).

Models
------

* Fix for consecutive photon generation models.
  (See `!193 <https://gitlab.com/esa/pyxel/-/merge_requests/193>`_).
* Add model Arctic.
  (See `!229 <https://gitlab.com/esa/pyxel/-/merge_requests/229>`_).
* Improve the speed of model 'charge_profile'.
  (See `!268 <https://gitlab.com/esa/pyxel/-/merge_requests/268>`_).
* Simple conversion model not working with dark frames.
  (See `!281 <https://gitlab.com/esa/pyxel/-/merge_requests/281>`_).

Others
------

* Use tryceratops for try and except styling.
  (See `!255 <https://gitlab.com/esa/pyxel/-/merge_requests/255>`_).
* Add a pipeline time profiling function.
  (See `!259 <https://gitlab.com/esa/pyxel/-/merge_requests/259>`_).
* Add unit tests for model 'charge_profile'.
  (See `!269 <https://gitlab.com/esa/pyxel/-/merge_requests/269>`_).
* Add unit tests for class 'Charge'.
  (See `!270 <https://gitlab.com/esa/pyxel/-/merge_requests/270.>`_).
* Add unit tests for function 'calibration.util.check_range.
  (See `!278 <https://gitlab.com/esa/pyxel/-/merge_requests/278.>`_).


version 0.10.2 / 2021-09-02
===========================

Core
----

* Enable logarithmic timing in dynamic mode.
  (See `!249 <https://gitlab.com/esa/pyxel/-/merge_requests/249>`_).

Others
------

* Fix issue with latest version of Mypy.
  (See `!253 <https://gitlab.com/esa/pyxel/-/merge_requests/253>`_).


version 0.10.1 / 2021-08-18
===========================

Core
----

* Add more debugging information when Calibration mode fails.
  (See `!228 <https://gitlab.com/esa/pyxel/-/merge_requests/228>`_).
* Add more debugging information in function 'get_obj_att'.
  (See `!243 <https://gitlab.com/esa/pyxel/-/merge_requests/243>`_).
* Separate configuration loader from scripts in 'inputs_outputs'.
  (See `!250 <https://gitlab.com/esa/pyxel/-/merge_requests/250>`_).

Documentation
-------------

* Install a specific conda package version.
  (See `!235 <https://gitlab.com/esa/pyxel/-/merge_requests/235>`_).

Others
------
* Resolved calibration not allowing one column text files
  (See `!233 <https://gitlab.com/esa/pyxel/-/merge_requests/233>`_).
* Update dependency to 'pygmo' from 2.11 to 2.16.1.
  (See `!234 <https://gitlab.com/esa/pyxel/-/merge_requests/234>`_).
* Use mypy version 0.812.
  (See `!247 <https://gitlab.com/esa/pyxel/-/merge_requests/247>`_).


version 0.10 / 2021-06-13
=========================

Core
----

* Add capability to save outputs of parametric mode as a xarray dataset.
  (See `!212 <https://gitlab.com/esa/pyxel/-/merge_requests/212>`_).
* Add capability to save calibration result dataset to disk from YAML.
  (See `!214 <https://gitlab.com/esa/pyxel/-/merge_requests/214>`_).
* Hide built-in Pyxel plotting capabilities (matplotlib figures from YAML).
  (See `!213 <https://gitlab.com/esa/pyxel/-/merge_requests/213>`_).
* dynamic mode progress bar.
  (See `!219 <https://gitlab.com/esa/pyxel/-/merge_requests/219>`_).
* Add capability to create models through command line using a template.
  (See `!217 <https://gitlab.com/esa/pyxel/-/merge_requests/217>`_).
* Improved dynamic mode.
  (See `!229 <https://gitlab.com/esa/pyxel/-/merge_requests/229>`_).
* Fix issue in creating parametric datasets.
  (See `!230 <https://gitlab.com/esa/pyxel/-/merge_requests/230>`_).

Documentation
-------------

* Update installation section.
  (See `!220 <https://gitlab.com/esa/pyxel/-/merge_requests/220>`_).
* Update documentation on parametric and dynamic mode.
  (See `!228 <https://gitlab.com/esa/pyxel/-/merge_requests/228>`_).

Models
------

* Fix TARS model.
  (See `!227 <https://gitlab.com/esa/pyxel/-/merge_requests/227>`_).
* Persistence model updated in charge_collection/persistence.py
  (See `!224 <https://gitlab.com/esa/pyxel/-/merge_requests/224>`_).

Others
------

* Fix circular import in parametric.py.
  (See `!216 <https://gitlab.com/esa/pyxel/-/merge_requests/216>`_).
* Add compatibility to Mypy 0.900.
  (See `!223 <https://gitlab.com/esa/pyxel/-/merge_requests/223>`_).


version 0.9.1 / 2021-05-17
==========================

Core
----

* Add missing packages when running 'pyxel.show_versions().
  (See `!193 <https://gitlab.com/esa/pyxel/-/merge_requests/193>`_).
* Fix issues with 'fsspec' version 0.9.
  (See `!198 <https://gitlab.com/esa/pyxel/-/merge_requests/198>`_).
* Refactoring class `Arguments.
  (See `!203 <https://gitlab.com/esa/pyxel/-/merge_requests/203>`_).
* Add new detector MKID. `Enrico Biancalani <https://gitlab.com/Dr_Bombero>`
  (See `!206 <https://gitlab.com/esa/pyxel/-/merge_requests/206>`_).

Others
------

* Fix issue when displaying current version.
  (See `!196 <https://gitlab.com/esa/pyxel/-/merge_requests/196>`_).
* Cannot import sub-packages 'calibration' and 'models.optics'.
  (See `!189 <https://gitlab.com/esa/pyxel/-/merge_requests/189>`_).
* Drop support for Python 3.6.
  (See `!199 <https://gitlab.com/esa/pyxel/-/merge_requests/199>`_).
* Solve typing issues with numpy.
  (See `!200 <https://gitlab.com/esa/pyxel/-/merge_requests/200>`_).
* Add functions to display calibration inputs and outputs in notebooks.
  (See `!194 <https://gitlab.com/esa/pyxel/-/merge_requests/194>`_).
* Fix issue with the latest click version and pipeline 'license'.
  (See `!208 <https://gitlab.com/esa/pyxel/-/merge_requests/208>`_).
* Resolve "Add 'LICENSE.txt' in MANIFEST.in".
  (See `!207 <https://gitlab.com/esa/pyxel/-/merge_requests/207>`_).


version 0.9 / 2021-03-25
========================

Core
----

* Fix a circular import in 'pyxel.data_structure'.
  (See `!171 <https://gitlab.com/esa/pyxel/-/merge_requests/171>`_).
* Add ability to download Pyxel examples from command line.
  (See `!176 <https://gitlab.com/esa/pyxel/-/merge_requests/176>`_).
* Add capability to read files from remote filesystems (e.g. http, ftp, ...).
  (See `!169 <https://gitlab.com/esa/pyxel/-/merge_requests/169>`_).
* Add a mechanism to set option in Pyxel.
  (See `!170 <https://gitlab.com/esa/pyxel/-/merge_requests/170>`_).
* Add capability to cache files in functions 'load_image' and 'load_data'.
  (See `!177 <https://gitlab.com/esa/pyxel/-/merge_requests/177>`_).
* Add a stripe pattern illumination model.
  (See `!174 <https://gitlab.com/esa/pyxel/-/merge_requests/174>`_).
* Add methods to display a Detector or an array of the Detector.
  (See `!173 <https://gitlab.com/esa/pyxel/-/merge_requests/173>`_).
* Initiate Processor object inside running mode functions.
  (See `!184 <https://gitlab.com/esa/pyxel/-/merge_requests/184>`_).
* Add HTML display methods for objects.
  (See `!185 <https://gitlab.com/esa/pyxel/-/merge_requests/185>`_).
* Add ability to display input image in the display_detector function.
  (See `!186 <https://gitlab.com/esa/pyxel/-/merge_requests/186>`_).
* Issue when creating islands in a Grid.
  (See `!188 <https://gitlab.com/esa/pyxel/-/merge_requests/188>`_).

Documentation
-------------

* Use the 'Documentation System'.
  (See `!178 <https://gitlab.com/esa/pyxel/-/merge_requests/178>`_).
* Use the 'Documentation System'.
  (See `!181 <https://gitlab.com/esa/pyxel/-/merge_requests/181>`_).
* Add an 'overview' page for each section in the documentation.
  (See `!183 <https://gitlab.com/esa/pyxel/-/merge_requests/183>`_).

Others
------

* Add a new badge for Binder.
  (See `!163 <https://gitlab.com/esa/pyxel/-/merge_requests/163>`_).
* Fix issue when generating documentation in CI/CD.
  (See `!179 <https://gitlab.com/esa/pyxel/-/merge_requests/179>`_).
* Always execute stage 'doc' in CI/CD.
  (See `!183 <https://gitlab.com/esa/pyxel/-/merge_requests/183>`_).
* Pyxel version cannot be retrieved.
  (See `!189 <https://gitlab.com/esa/pyxel/-/merge_requests/189>`_).
* Remove pyviz from dependencies.
  (See `!191 <https://gitlab.com/esa/pyxel/-/merge_requests/191>`_).

Pipelines
---------

* Calibration - Export champions for every evolution and every island.
  (See `!164 <https://gitlab.com/esa/pyxel/-/merge_requests/164>`_).
* Calibration - Extract best individuals.
  (See `!165 <https://gitlab.com/esa/pyxel/-/merge_requests/165>`_).
* Calibration - Fix an issue when extracting parameters.
  (See `!166 <https://gitlab.com/esa/pyxel/-/merge_requests/166>`_).


version 0.8.1 / 2021-01-26
==========================

Documentation
-------------

* Enabled sphinxcontrib-bibtex version 2.
  (See `#155 <https://gitlab.com/esa/pyxel/-/issues/155>`_).

Others
------

* Add a new badge for Google Group.
  (See `!157 <https://gitlab.com/esa/pyxel/-/merge_requests/157>`_).
* Prepare Pyxel to be uploadable on PyPI.
  (See `!161 <https://gitlab.com/esa/pyxel/-/merge_requests/161>`_).


version 0.8 / 2020-12-11
========================

Core
----

* Improved user friendliness.
  (See `#144 <https://gitlab.com/esa/pyxel/issues/144>`_).
* Simplified the look of YAML configuration files.
  (See `#118 <https://gitlab.com/esa/pyxel/issues/118>`_).
* Extracted functions to run modes separately from pyxel.run.run()
  (See `#61 <https://gitlab.com/esa/pyxel/issues/61>`_).
* Refactored YAML loader, returns a class Configuration instead of a dictionary.
  (See `#60 <https://gitlab.com/esa/pyxel/issues/60>`_).
* Created new classes Single and Dynamic to store running mode parameters.
  (See `#121 <https://gitlab.com/esa/pyxel/issues/121>`_).
* Split class Outputs for different modes and moved to inputs_ouputs.
  (See `#149 <https://gitlab.com/esa/pyxel/issues/149>`_).
* Added a simple Inter Pixel Capacitance model for CMOS detectors.
  (See `#65 <https://gitlab.com/esa/pyxel/issues/65>`_).
* Added a model for the amplifier crosstalk.
  (See `#116 <https://gitlab.com/esa/pyxel/issues/116>`_).
* Added ability to load custom QE maps.
  (See `#117 <https://gitlab.com/esa/pyxel/issues/117>`_).
* Use 'Dask' for Calibration mode.
  (See `!145 <https://gitlab.com/esa/pyxel/-/merge_requests/145>`_).

Others
------

* Change licence to MIT.
  (See `!142 <https://gitlab.com/esa/pyxel/-/merge_requests/142>`_).
* Change Pyxel's package name to 'pyxel-sim'.
  (See `!144 <https://gitlab.com/esa/pyxel/-/merge_requests/114>`_).
* Added a 'How to release' guide.
  (See `#109 <https://gitlab.com/esa/pyxel/issues/109>`_).
* Remove_folder_examples_data.
  (See `!148 <https://gitlab.com/esa/pyxel/-/merge_requests/148>`_).
* Fix typo in documentation.
  (See `!149 <https://gitlab.com/esa/pyxel/-/merge_requests/149>`_).
* Updated documentation according to v0.8.
  (See `!153 <https://gitlab.com/esa/pyxel/-/merge_requests/153>`_).


version 0.7 / 2020-10-22
========================

Core
----

* Update .gitignore file.
  (See `!123 <https://gitlab.com/esa/pyxel/-/merge_requests/123>`_).
* Added capability to load more image formats and tests.
  (See `!113 <https://gitlab.com/esa/pyxel/-/merge_requests/113>`_).
* Create a function 'pyxel.show_versions().
  (See `!114 <https://gitlab.com/esa/pyxel/-/merge_requests/114>`_).
* Shorter path to import/reference the models.
  (See `!126 <https://gitlab.com/esa/pyxel/-/merge_requests/126>`_).
* Remove deprecated methods from Photon class.
  (See `!119 <https://gitlab.com/esa/pyxel/-/merge_requests/119>`_).
* Instances of 'DetectionPipeline' are not serializable.
  (See `!120 <https://gitlab.com/esa/pyxel/-/merge_requests/120>`_).
* Cannot run 'calibration' pipeline with multiprocessing or ipyparallel islands.
  (See `!121 <https://gitlab.com/esa/pyxel/-/merge_requests/121>`_).
* Make package and script 'pyxel' executable.
  (See `!112 <https://gitlab.com/esa/pyxel/-/merge_requests/112>`_).
* Created a function inputs_outputs.load_table().
  (See `!132 <https://gitlab.com/esa/pyxel/-/merge_requests/132>`_).
* Reimplement convolution in POPPY optical_psf model.
  (See `#52 <https://gitlab.com/esa/pyxel/issues/52>`_).
* Add property 'Detector.numbytes' and/or method 'Detector.memory_usage()'
  (See `!116 <https://gitlab.com/esa/pyxel/-/merge_requests/116>`_).
* Created jupyxel.py for jupyter notebook visualization.
  (See `!122 <https://gitlab.com/esa/pyxel/-/merge_requests/122>`_).

Documentation
-------------

* Remove comments for magic methods.
  (See `!127 <https://gitlab.com/esa/pyxel/-/merge_requests/127>`_).


version 0.6 / 2020-09-16
========================

* Improved contributing guide
  (See `#68 <https://gitlab.com/esa/pyxel/issues/68>`_).
* Remove file '.gitlab-ci-doc.yml'
  (See `#73 <https://gitlab.com/esa/pyxel/issues/73>`_).
* Change license and add copyrights to all source files.
  (See `#69 <https://gitlab.com/esa/pyxel/issues/69>`_).
* Fix issues with example file 'examples/calibration_CDM_beta.yaml'.
  (See `#75 <https://gitlab.com/esa/pyxel/issues/75>`_).
* Fix issues with example file 'examples/calibration_CDM_irrad.yaml'.
  (See `#76 <https://gitlab.com/esa/pyxel/issues/76>`_).
* Updated Jupyter notebooks examples.
  (See `#87 <https://gitlab.com/esa/pyxel/issues/87>`_).
* Apply command 'isort' to the code base.
* Refactor class `ParametricPlotArgs`.
  (See `#77 <https://gitlab.com/esa/pyxel/issues/77>`_).
* Create class `SinglePlot`.
  (See `#78 <https://gitlab.com/esa/pyxel/issues/78>`_).
* Create class `CalibrationPlot`.
  (See `#79 <https://gitlab.com/esa/pyxel/issues/79>`_).
* Create class `ParametricPlot`.
  (See `#80 <https://gitlab.com/esa/pyxel/issues/80>`_).
* Add templates for bug report, feature request and merge request.
  (See `#105 <https://gitlab.com/esa/pyxel/issues/105>`_).
* Parallel computing for 'parametric' mode.
  (See `#111 <https://gitlab.com/esa/pyxel/issues/111>`_).
* Improved docker image.
  (See `#96 <https://gitlab.com/esa/pyxel/issues/96>`_).
* Fix calibration pipeline.
  (See `#113 <https://gitlab.com/esa/pyxel/issues/113>`_).
* CI/CD pipeline 'licenses-latests' fails.
  (See `#125 <https://gitlab.com/esa/pyxel/issues/125>`_).


version 0.5 / 2019-12-20
========================

* Clean-up code.
* Remove any dependencies to esapy_config
  (See `#54 <https://gitlab.com/esa/pyxel/issues/54>`_).
* Refactor charge generation models to avoid code duplication
  (See `#49 <https://gitlab.com/esa/pyxel/issues/49>`_).
* Implement multi-threaded/multi-processing mode
  (See `#44 <https://gitlab.com/esa/pyxel/issues/44>`_).


version 0.4 / 2019-07-09
========================

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
========================

* Single and Parametric mode have been implemented
* Infrastructure code has been placed in 2 new projects: esapy_config and esapy_web
* Web interface (GUI) is dynamically generated based on attrs definitions
* NGHxRG noise generator model has been added

version 0.2 / 2018-01-18
========================

* TARS cosmic ray model has been reimplemented and added

version 0.1 / 2018-01-10
========================

* Prototype: first pipeline for a CCD detector
