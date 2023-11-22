# Changelog
Pyxel version numbers are in the of form x.y.z.

- The major release number (x) is incremented if a feature release includes a significant
backward incompatible change that affects a significant fraction of users.
- The minor release number (y) is incremented on each feature release.
Minor releases include updated stdlib stubs from typeshed.
- The point release number (z) is incremented when there are fixes only.

Pyxel doesn't use SemVer anymore, since most minor releases have at least minor backward incompatible changes.

## UNRELEASED
This release brings a number of bugfixes, documentation and improvements.

### Core
* Removed deprecated `Detector.set_output_dir` method and `Detector.output_dir` property.
  (See [!759](https://gitlab.com/esa/pyxel/-/merge_requests/759)).
* Image data bucket only allows integer data.
  (See [!764](https://gitlab.com/esa/pyxel/-/merge_requests/764)).
* Fix issue in Observation mode with a 2D parameter.
  (See [!770](https://gitlab.com/esa/pyxel/-/merge_requests/770)).
* Changed Array class initializer. The internal array is initialized to None not np.zeroes. 
  (See [!767](https://gitlab.com/esa/pyxel/-/merge_requests/767)).
* Remove attribute `input_image` from `Detector`.
  (See [!772](https://gitlab.com/esa/pyxel/-/merge_requests/772)).
* Fix issue in `Array.__repr__`.
  (See [!773](https://gitlab.com/esa/pyxel/-/merge_requests/773)).

### Documentation

### Models
* Improvements in model 'pulse_processing' in Model group 'phasing'.
  (See [!665](https://gitlab.com/esa/pyxel/-/merge_requests/665)).
* Model 'amplifier_crosstalk' is moved from 'readout_electronics' to 'charge_measurement'.
  (See [!763](https://gitlab.com/esa/pyxel/-/merge_requests/763)).
* Remove warnings from model 'Cosmix' from 'Charge Generation.
  (See [!768](https://gitlab.com/esa/pyxel/-/merge_requests/768)).
* Remove all warnings in dark current model.
  (See [!769](https://gitlab.com/esa/pyxel/-/merge_requests/769)).

### Others
* Minor refactoring.
  (See [!756](https://gitlab.com/esa/pyxel/-/merge_requests/756)).
* Check more packages with function `pyxel.show_versions()`.
  (See [!757](https://gitlab.com/esa/pyxel/-/merge_requests/757)).
* Fix issues when running Mypy 1.7.
  (See [!762](https://gitlab.com/esa/pyxel/-/merge_requests/762)).


## 1.12 / 2023-10-27
This release brings a number of bugfixes, documentation and improvements.

The function `pyxel.display_detector` used in the jupyter notebooks to visualise the detector at each stage of the 
pipeline, has now the option to display in logarithmic scale besides the linear scale and to change the color of the image.
The bin size and the x-axis range can now be changed in the related historgram plot.

### Core
* In 'Custom Observation' mode, add a sanity test to verify input custom data.
  (See [!749](https://gitlab.com/esa/pyxel/-/merge_requests/749)).
* Nan output and missing output in observation mode.
  (See [!750](https://gitlab.com/esa/pyxel/-/merge_requests/750)).
* Improved function `pyxel.display_detector`.
  (See [!739](https://gitlab.com/esa/pyxel/-/merge_requests/739)).
* Add filter to ignore warnings in scene_generation.
  (See [!751](https://gitlab.com/esa/pyxel/-/merge_requests/751)).
* Reduce warning in dark current model.
  (See [!643](https://gitlab.com/esa/pyxel/-/merge_requests/643)).

### Documentation
* Add more information about the Conda environments in the 
  [installation documentation](https://esa.gitlab.io/pyxel/doc/stable/tutorials/install.html).
  (See [!746](https://gitlab.com/esa/pyxel/-/merge_requests/746)).
* Add documentation for ModelGroup 'Scene Generation'.
  (See [!752](https://gitlab.com/esa/pyxel/-/merge_requests/752)).


## 1.11.1 / 2023-10-19

This release brings one bugfix.

### Others
* Remove Scopesim as a dependency of Pyxel.
  (See [!745](https://gitlab.com/esa/pyxel/-/merge_requests/745)).

## 1.11 / 2023-10-18
This release brings a number of bugfixes, documentation and improvements.

The following new models were added:
* [`load_star_map`](https://esa.gitlab.io/pyxel/doc/latest/references/model_groups/scene_generation_models.html#pyxel.models.scene_generation.load_star_map) in `Scene Generation`.
* [`simple_aperture`](https://esa.gitlab.io/pyxel/doc/latest/references/model_groups/photon_collection_models.html#pyxel.models.photon_collection.simple_aperture) in `Photon Collection`.

Parameter `data_type` is now optional in model 
[`simple_adc`](https://esa.gitlab.io/pyxel/doc/latest/references/model_groups/readout_electronics.html#pyxel.models.readout_electronics.simple_adc) 
in `Readout Electronics`.
If this parameter is not provided then it is inferred from `adc_bit_resolution` in `Detector`.

### Core
* Bug when using with a configuration file with extension '.yml' instead of '.yaml'.
  (See [!737](https://gitlab.com/esa/pyxel/-/merge_requests/737)).
* Speedup function [`pyxel.load`](https://esa.gitlab.io/pyxel/doc/latest/references/api/configuration.html#pyxel.load).
  (See [!738](https://gitlab.com/esa/pyxel/-/merge_requests/738)).
* Add `Scene` to `pyxel.run_mode`.
  (See [!740](https://gitlab.com/esa/pyxel/-/merge_requests/740)).
* Fix bug with the output of [`pyxel.run_mode`](https://esa.gitlab.io/pyxel/doc/latest/references/api/run.html#pyxel.run_mode).
  The 'image' container has type `float64` instead of `int`.
  (See [!742](https://gitlab.com/esa/pyxel/-/merge_requests/742)).

### Documentation
* Add info about Jupyter book being not interactive.
  (See [!726](https://gitlab.com/esa/pyxel/-/merge_requests/726)).
* Add new icon/badge 'I want to contribute !'
  (See [!727](https://gitlab.com/esa/pyxel/-/merge_requests/727)).
* Update EMCCD cic model [`multiplication_register_cic`](https://esa.gitlab.io/pyxel/doc/latest/references/model_groups/charge_transfer_models.html#pyxel.models.charge_transfer.multiplication_register_cic)
  in `Charge Transfer`.
  (See [!728](https://gitlab.com/esa/pyxel/-/merge_requests/728)).
* Fix documentation for model [`load_charge`](https://esa.gitlab.io/pyxel/doc/latest/references/model_groups/charge_generation_models.html#pyxel.models.charge_generation.load_charge) 
  in `charge_generation`.
  (See [!743](https://gitlab.com/esa/pyxel/-/merge_requests/743)).

### Models
* Add first model for group [`load_star_map`](https://esa.gitlab.io/pyxel/doc/latest/references/model_groups/scene_generation_models.html#pyxel.models.scene_generation.load_star_map)
  in `Scene Generation`.
  (See [!715](https://gitlab.com/esa/pyxel/-/merge_requests/715)
  and [!716](https://gitlab.com/esa/pyxel/-/merge_requests/716)).
* Fix unexpected value in [`simple_adc`](https://esa.gitlab.io/pyxel/doc/latest/references/model_groups/readout_electronics.html#pyxel.models.readout_electronics.simple_adc)
  in `Readout Electronics`.
  (See [!732](https://gitlab.com/esa/pyxel/-/merge_requests/732)).
* Add model [`simple_aperture`](https://esa.gitlab.io/pyxel/doc/latest/references/model_groups/photon_collection_models.html#pyxel.models.photon_collection.simple_aperture)
  in `Photon Collection` to convert from scene to photon.
  (See [!733](https://gitlab.com/esa/pyxel/-/merge_requests/733)).
* Parameter `data_type` is optional in model [`simple_adc`](https://esa.gitlab.io/pyxel/doc/latest/references/model_groups/readout_electronics.html#pyxel.models.readout_electronics.simple_adc)
  in `Readout Electronics`.
  (See [!736](https://gitlab.com/esa/pyxel/-/merge_requests/736)).
* Rename induced dark_current model to [`radiation induced dark current`](https://esa.gitlab.io/pyxel/doc/stable/references/model_groups/charge_generation_models.html#radiation-induced-dark-current).
  (See [!731](https://gitlab.com/esa/pyxel/-/merge_requests/731)).

### Others
* Fix issues with mypy and Matplotlib 3.8.
  (See [!734](https://gitlab.com/esa/pyxel/-/merge_requests/734)).
* Add [`poppy`](https://poppy-optics.readthedocs.io/) as a dependency in Conda.
  (See [!741](https://gitlab.com/esa/pyxel/-/merge_requests/741)).


## 1.10.2 / 2023-08-29
This release brings a bugfix with the conda package.


## 1.10.1 / 2023-08-28
This release brings a bugfix.

### Others
* Update lacosmic dependency to optional.
  (See [!721](https://gitlab.com/esa/pyxel/-/merge_requests/721)).

## 1.10 / 2023-08-28

This release brings a number of bugfixes, documentation and improvements.

The [Pixel Coordinate conventions](https://esa.gitlab.io/pyxel/doc/latest/background/pixel_coordinate_conventions.html#pixel-coordinate-conventions) 
is now clarified.

The following new models were added:
* [`Wavelength dependence AIRS`](https://esa.gitlab.io/pyxel/doc/latest/references/model_groups/photon_collection_models.html#wavelength-dependence-airs)
  from CEA Paris-Saclay.
* [`Dark Current induced`](https://esa.gitlab.io/pyxel/doc/latest/references/model_groups/charge_generation_models.html#dark-current-induced)
  from ISAE Supaero.
* [`EMCCD Clock Induced Charge`](https://esa.gitlab.io/pyxel/doc/latest/references/model_groups/charge_transfer_models.html#emccd-clock-induced-charge-cic) 
  from Niels Bohr Institute and University of Copenhagen.
* [`Remove Cosmic Rays`](https://esa.gitlab.io/pyxel/doc/latest/references/model_groups/data_processing_models.html#remove-cosmic-rays).
* [`Signal to Noise Ratio`](https://esa.gitlab.io/pyxel/doc/latest/references/model_groups/data_processing_models.html#pyxel.models.data_processing.signal_to_noise_ratio).


A new parameter `with_intermediate_steps` in function [`pyxel.run_mode`](https://esa.gitlab.io/pyxel/doc/latest/references/api/run.html#pyxel.run_mode)
has been added. With this parameter, it is now possible to display all intermediate steps executed in the
pipeline. This parameter is provisional and may change in the future.

### Breaking changes

Bucket `Detector.processed_data` is removed. This bucket was used in the 
[Data Processing](https://esa.gitlab.io/pyxel/doc/stable/background/pipeline.html) group
and is now replaced by the `Detector.data` bucket.

### Core
* Remove data structure `ProcessedData` and bucket `Detector.processed_data`.
  (See [!693](https://gitlab.com/esa/pyxel/-/merge_requests/693)).
* Add parameter `with_intermediate_steps` in function 
  [`pyxel.run_mode`](https://esa.gitlab.io/pyxel/doc/latest/references/api/run.html#pyxel.run_mode).
  (See [!687](https://gitlab.com/esa/pyxel/-/merge_requests/687)).
* Get full size 'simulated' and 'target' image when running a Calibration pipeline
  with [`pyxel.run_mode`](https://esa.gitlab.io/pyxel/doc/latest/references/api/run.html#pyxel.run_mode).
  (See [!695](https://gitlab.com/esa/pyxel/-/merge_requests/695)).
* Fix KeyError issue with function
  [`pyxel.display_simulated`](https://esa.gitlab.io/pyxel/doc/latest/references/api/notebook.html#pyxel.display_simulated).
  (See [!696](https://gitlab.com/esa/pyxel/-/merge_requests/696)).
* Fix issue when running Calibration mode with weight files 
  with [`pyxel.run_mode`](https://esa.gitlab.io/pyxel/doc/latest/references/api/run.html#pyxel.run_mode).
  (See [!700](https://gitlab.com/esa/pyxel/-/merge_requests/700)).
* Wrong shape when using parameters 'result_fit_range' and 'target_fit_range' in Calibration mode.
  (See [!701](https://gitlab.com/esa/pyxel/-/merge_requests/701)).
* Simplify outputs of [`pyxel.run_mode`](https://esa.gitlab.io/pyxel/doc/latest/references/api/run.html#pyxel.run_mode)
  in [Exposure mode](https://esa.gitlab.io/pyxel/doc/latest/background/running_modes/exposure_mode.html).
  (See [!702](https://gitlab.com/esa/pyxel/-/merge_requests/702) and [!709](https://gitlab.com/esa/pyxel/-/merge_requests/709)).
* Refactor class [`ReadoutProperties`](https://esa.gitlab.io/pyxel/doc/latest/references/api/detectorproperties.html#pyxel.detectors.ReadoutProperties).
  (See [!705](https://gitlab.com/esa/pyxel/-/merge_requests/705)).

### Documentation
* Add questions to [FAQ](https://esa.gitlab.io/pyxel/doc/latest/about/FAQ.html).
  (See [!688](https://gitlab.com/esa/pyxel/-/merge_requests/688) and [!692](https://gitlab.com/esa/pyxel/-/merge_requests/692)).
* Data link missing. Add link to `DataTree`.
  (See [!676](https://gitlab.com/esa/pyxel/-/merge_requests/676)).
* Add documentation for methods `.plot()` and `.to_xarray()` for `Pixel`, `Photon`, `Signal`, `Image` and `Phase`.
  (See [!533](https://gitlab.com/esa/pyxel/-/merge_requests/533)).
* Add more info in documentation about [`Data Processing`](https://esa.gitlab.io/pyxel/doc/latest/references/model_groups/data_processing_models.html)
  models. (See [!640](https://gitlab.com/esa/pyxel/-/merge_requests/640)).

### Models
* New model [`Wavelength dependence AIRS`](https://esa.gitlab.io/pyxel/doc/latest/references/model_groups/photon_collection_models.html#wavelength-dependence-airs)
  in [`Photon Collection`](https://esa.gitlab.io/pyxel/doc/latest/references/model_groups/photon_collection_models.html)
  from CEA Paris Saclay.
  (See [!677](https://gitlab.com/esa/pyxel/-/merge_requests/677)).
* Refactor [`EMCCD multiplication register`](https://esa.gitlab.io/pyxel/doc/latest/references/model_groups/charge_transfer_models.html#emccd-model) 
  model in [`Charge Transfer`](https://esa.gitlab.io/pyxel/doc/latest/references/model_groups/charge_transfer_models.html) with clock-induced-charges (CIC).
  (See [!678](https://gitlab.com/esa/pyxel/-/merge_requests/678)).
* New model of [`Dark Current induced`](https://esa.gitlab.io/pyxel/doc/latest/references/model_groups/charge_generation_models.html#dark-current-induced)
  in [`Charge Geneneration`](https://esa.gitlab.io/pyxel/doc/latest/references/model_groups/charge_generation_models.html).
  This model was developed by ISAE Supaero.
  (See [!698](https://gitlab.com/esa/pyxel/-/merge_requests/698)).
* New data processing model [`Remove Cosmic Rays`](https://esa.gitlab.io/pyxel/doc/latest/references/model_groups/data_processing_models.html#remove-cosmic-rays)
  in [`Data Processing`](https://esa.gitlab.io/pyxel/doc/latest/references/model_groups/data_processing_models.html).
  (See [!685](https://gitlab.com/esa/pyxel/-/merge_requests/685)).
* New [`Signal to Noise Ratio`](https://esa.gitlab.io/pyxel/doc/latest/references/model_groups/data_processing_models.html#pyxel.models.data_processing.signal_to_noise_ratio) model
  in [`Data Processing`](https://esa.gitlab.io/pyxel/doc/latest/references/model_groups/data_processing_models.html).
  (See [!707](https://gitlab.com/esa/pyxel/-/merge_requests/707)).
* Use new Pyxel Coordinate Conventions for model [`Load Charge`](https://esa.gitlab.io/pyxel/doc/latest/references/model_groups/charge_generation_models.html#load-charge)
  in [`Charge Geneneration`](https://esa.gitlab.io/pyxel/doc/latest/references/model_groups/charge_generation_models.html).
  (See [!717](https://gitlab.com/esa/pyxel/-/merge_requests/717)).

### Others
* Refactoring.
  (See [!682](https://gitlab.com/esa/pyxel/-/merge_requests/682)).
* Reduce code complexity by enabling McCabe plugin ruff.
  (See [!257](https://gitlab.com/esa/pyxel/-/merge_requests/257)).
* Add rule 'pep8-naming' to 'ruff'.
  (See [!699](https://gitlab.com/esa/pyxel/-/merge_requests/699)).
* Fix coverage and generate an [HTML report](https://esa.gitlab.io/pyxel/htmlcov/).
  (See [!704](https://gitlab.com/esa/pyxel/-/merge_requests/704)
  and [!706](https://gitlab.com/esa/pyxel/-/merge_requests/706)).
* Fix issue E721 found by flake8 version 6.1.0.
  (See [!708](https://gitlab.com/esa/pyxel/-/merge_requests/708)).
* Apply 'ruff' to folder 'tests'.
  (See [!718](https://gitlab.com/esa/pyxel/-/merge_requests/718)).

## 1.9.1 / 2023-07-07

This release brings a number of bugfixes.

### Models
* Fix an error in a formula for model 'dead_time' in 'readout_electronics'.
  (See [!681](https://gitlab.com/esa/pyxel/-/merge_requests/681)).
* New model 'Wavelength dependence AIRS' for 'Photon Collection'.
  (See [!677](https://gitlab.com/esa/pyxel/-/merge_requests/677)).

### Others
* Cannot load a FITS file from an HTTP URL.
  (See [!672](https://gitlab.com/esa/pyxel/-/merge_requests/672)).
* Refactoring.
  (See [!679](https://gitlab.com/esa/pyxel/-/merge_requests/679)).

## 1.9 / 2023-06-01

This release brings a number of bugfixes and documentation improvements.

`Detector` contains a new bucket `data` which contains a `xarray.DataTree` 
(see [!631](https://gitlab.com/esa/pyxel/-/merge_requests/631))

### Breaking changes

Function [`pyxel.run_mode`](https://esa.gitlab.io/pyxel/doc/latest/references/api/run.html#pyxel.run_mode) is not (yet) stable and may change.

Support for Python 3.8 has been dropped and support for Python 3.11 has been added.

The minimum versions of some dependencies were changed:

  | Package | Old   | New        |
  |---------|-------|------------|
  | Python  | 3.8+  | **3.9+**   |
  | Poppy   | 1.0.3 | **1.1.0+** |

### Core
* Use `xarray.DataTree` for a new `Detector.data` bucket.
  (See [!631](https://gitlab.com/esa/pyxel/-/merge_requests/631)).
* Function [`pyxel.run_mode`](https://esa.gitlab.io/pyxel/doc/latest/references/api/run.html#pyxel.run_mode) returns a `DataTree`.
  (See [!647](https://gitlab.com/esa/pyxel/-/merge_requests/647)).
* Refactoring method `Calibration.run_calibration_new`.
  (See [!661](https://gitlab.com/esa/pyxel/-/merge_requests/661) and
  [!663](https://gitlab.com/esa/pyxel/-/merge_requests/663)).
* Fix issue in function [`pyxel.run_mode`](https://esa.gitlab.io/pyxel/doc/latest/references/api/run.html#pyxel.run_mode).
  (See [!669](https://gitlab.com/esa/pyxel/-/merge_requests/669)).
* Improve Calibration mode when using [`pyxel.run_mode`](https://esa.gitlab.io/pyxel/doc/latest/references/api/run.html#pyxel.run_mode).
  (See [!666](https://gitlab.com/esa/pyxel/-/merge_requests/666)).

### Documentation
* The general documentation has been reviewed and minor fixes made such as:
  spelling mistakes, typos in markup, grammatical issues, dead hyperlinks,
  and wording simplification.
  (see [!579](https://gitlab.com/esa/pyxel/-/merge_requests/579)).
* Fix documentation for 'JSON Schema'.
  (see [!648](https://gitlab.com/esa/pyxel/-/merge_requests/648)).
* Update [JSON Schema Documentation](https://esa.gitlab.io/pyxel/doc/stable/howto/json_schema.html).
  (see [!649](https://gitlab.com/esa/pyxel/-/merge_requests/649)).
* Fix typing information for model '[charge_generation.charge_deposition](https://esa.gitlab.io/pyxel/doc/stable/references/model_groups/charge_generation_models.html#charge-deposition-model)'.
  (see [!652](https://gitlab.com/esa/pyxel/-/merge_requests/652)).
* Add more documentation for '[data_processing](https://esa.gitlab.io/pyxel/doc/stable/references/model_groups/data_processing_models.html)' 
  models '[mean_variance](https://esa.gitlab.io/pyxel/doc/stable/references/model_groups/data_processing_models.html#mean-variance)'
  and '[linear_regression](https://esa.gitlab.io/pyxel/doc/stable/references/model_groups/data_processing_models.html#linear-regression)'.
  (see [!660](https://gitlab.com/esa/pyxel/-/merge_requests/660)).
* Fix documentation.
  (see [!668](https://gitlab.com/esa/pyxel/-/merge_requests/668)).

### Models
* New data processing model '[data_processing.mean-variance](https://esa.gitlab.io/pyxel/doc/stable/references/model_groups/data_processing_models.html#mean-variance)'.
  (See [!645](https://gitlab.com/esa/pyxel/-/merge_requests/645)).
* Improve '[data_processing.statistics](https://esa.gitlab.io/pyxel/doc/stable/references/model_groups/data_processing_models.html#statistics)' model usage.
  (See [!646](https://gitlab.com/esa/pyxel/-/merge_requests/646)).
* Improved model '[charge_measurement.physical_non_linearity_with_saturation](https://esa.gitlab.io/pyxel/doc/stable/references/model_groups/charge_measurement_models.html#pyxel.models.charge_measurement.physical_non_linearity_with_saturation)'.
  (See [!655](https://gitlab.com/esa/pyxel/-/merge_requests/655)).
* Add new model '[data_processing.linear_regression](https://esa.gitlab.io/pyxel/doc/stable/references/model_groups/data_processing_models.html#linear-regression)'.
  (See [!658](https://gitlab.com/esa/pyxel/-/merge_requests/658)).
* Fix issues with '[data_processing.linear_regression](https://esa.gitlab.io/pyxel/doc/stable/references/model_groups/data_processing_models.html#linear-regression)' model.
  (See [!670](https://gitlab.com/esa/pyxel/-/merge_requests/670)).
* Add unit tests to models in model group data processing.
  (See [!703](https://gitlab.com/esa/pyxel/-/merge_requests/703)).

### Others
* Remove support to Python 3.8.
  (See [!633](https://gitlab.com/esa/pyxel/-/merge_requests/633)).
* Add units to data buckets in display detector.
  (See [!641](https://gitlab.com/esa/pyxel/-/merge_requests/641)).
* Adding more linter rules to 'ruff'.
  (See [!644](https://gitlab.com/esa/pyxel/-/merge_requests/644)).
* Fix CI/CD pipelines.
  (See [!650](https://gitlab.com/esa/pyxel/-/merge_requests/650)).
* Add compatibility to Python 3.11.
  (See [!651](https://gitlab.com/esa/pyxel/-/merge_requests/651)).
* Move and update 'requirements-dev.txt'.
  (See [!654](https://gitlab.com/esa/pyxel/-/merge_requests/654)).
* Fixed Windows compatibility issue with several tests.
  (See [!655](https://gitlab.com/esa/pyxel/-/merge_requests/655)).
* Add missing packages in [`pyxel.show_versions()`](https://esa.gitlab.io/pyxel/doc/latest/references/api/run.html#pyxel.show_versions).
  (See [!657](https://gitlab.com/esa/pyxel/-/merge_requests/657)).
* Poppy version 1.0.3 is not compatible with numpy 1.24.
  (See [!659](https://gitlab.com/esa/pyxel/-/merge_requests/659)).
* Remove noisy error messages when using 'tox'.
  (See [!662](https://gitlab.com/esa/pyxel/-/merge_requests/662)).


## 1.8 / 2023-03-30

This release brings a number of bugfixes and documentation improvements.

A new function `pyxel.run_mode` has been added and will replace `pyxel.exposure_mode`, `pyxel.observation_mode`
and `pyxel.calibration_mode` functions. This function `pyxel.run_mode` always returns an Xarray `Dataset`

A new parameter `custom_dir_name` has been added to customize the name of the output folder.

Example of a configuration file: 
```yaml
exposure:   # This is also valid for 'observation:' and 'calibration:'
  outputs:
    output_folder: output
    custom_dir_name: custom    # <= NEW
    save_data_to_file:
```
In this example, a new output folder `output/custom_...` will be created.


In the calibration configuration files, it is now possible to add different boundaries for values defined as a list.

Example of configuration file before:
```yaml
parameters:   
  - key:              pipeline.charge_transfer.cdm.arguments.beta
    values:           _
    logarithmic:      false
    boundaries:       [0.1, 0.9]
  - key:              pipeline.charge_transfer.cdm.arguments.trap_release_times
    values:           [_, _, _, _]
    logarithmic:      true
    boundaries:       [1.e-5, 1.e-1]   # Same boundaries for the four values
  - key:              pipeline.charge_transfer.cdm.arguments.trap_densities
    values:           [_, _, _, _]
    logarithmic:      true
    boundaries:       [1.e-2, 1.e+2]   # Same boundaries for the four values
```

and after:
```yaml
parameters:   
  - key:              pipeline.charge_transfer.cdm.arguments.beta
    values:           _
    logarithmic:      false
    boundaries:       [0.1, 0.9]
  - key:              pipeline.charge_transfer.cdm.arguments.trap_release_times
    values:           [_, _, _, _]
    logarithmic:      true
    boundaries:       [1.e-5, 1.e-1]   # Same boundaries for the four values
  - key:              pipeline.charge_transfer.cdm.arguments.trap_densities
    values:           [_, _, _, _]
    logarithmic:      true
    boundaries:                       # NEW different boundaries for the four values
      - [1.e-2, 1.e+2]
      - [1.e-3, 1.e+3]
      - [1.e-4, 1.e+4]
      - [1.e-5, 1.e+5]
```

### Breaking changes

The minimum versions of some dependencies were changed:

  | Package | Old   | New         |
  |---------|-------|-------------| 
  | numpy   | 1.20  | **1.21**    |
  | xarray  | 0.19  | **2022.06** |

### Core
* Multiple boundary conditions for calibration mode.
  It's now possible to add different boundaries condition
  (See [!612](https://gitlab.com/esa/pyxel/-/merge_requests/612)).
* Add a option to force data type in function 'load_table'.
  (See [!615](https://gitlab.com/esa/pyxel/-/merge_requests/615)).
* Observation mode, build table with string not only float.
  (See [!613](https://gitlab.com/esa/pyxel/-/merge_requests/613)).
* Check that in exposure readout time is strictly increasing.
  (See [!516](https://gitlab.com/esa/pyxel/-/merge_requests/516)).
* Improve Calibration Dataset output.
  (See [!624](https://gitlab.com/esa/pyxel/-/merge_requests/624)).
* Add new function 'pyxel.run_mode'.
  (See [!623](https://gitlab.com/esa/pyxel/-/merge_requests/623) 
  and [!630](https://gitlab.com/esa/pyxel/-/merge_requests/630)).
* Fix warning message in Calibration.
  (See [!625](https://gitlab.com/esa/pyxel/-/merge_requests/625)).
* Add charge detector bucket to xarray output when charge is not a dataframe.
  (See [!629](https://gitlab.com/esa/pyxel/-/merge_requests/629)).
* Add photon and charge buckets also to calibration mode.
  (See [!632](https://gitlab.com/esa/pyxel/-/merge_requests/632)).
* Ability to name the outputs instread of timestamp directory creation.
  (See [!211](https://gitlab.com/esa/pyxel/-/merge_requests/211)).

### Documentation
* Use 'Sphinx 5' and 'Sphinx Book Theme 1'.
  (See [!621](https://gitlab.com/esa/pyxel/-/merge_requests/621)).
* Update links in Documentation Tutorials & Examples.
  (See [!628](https://gitlab.com/esa/pyxel/-/merge_requests/628)).

### Models
* Add new 'Source Extractor' for 'Data Processing' model group.
  (See [!634](https://gitlab.com/esa/pyxel/-/merge_requests/634)).

### Others
* Set minimum version of numpy to 1.21.
  (See [!614](https://gitlab.com/esa/pyxel/-/merge_requests/614)).
* Use 'ruff' in CI/CD.
  (See [!616](https://gitlab.com/esa/pyxel/-/merge_requests/616)).
* Add compatibility to Pandas 2.0.
  (See [!627](https://gitlab.com/esa/pyxel/-/merge_requests/627)).

 
## 1.7 / 2023-02-09

This release brings a number of bugfixes and documentation improvements.

The first peer-reviewed paper of Pyxel was published in the 
[Journal of Astronomical Telescops, Instruments, and Systems](https://doi.org/10.1117/1.JATIS.8.4.048002) 
and Pyxel has now an entry in the [Astrophysics Source Code Library](https://ascl.net/2301.002).

A new model group 'Photon Collection' was added to replace the groups 'Photon Generation' and 'Optics'.
All models from 'Photon Generation' and 'Optics' are copied into 'Photon Collection'.
The current models from 'Photon Generation' and 'Optics' are obsolete/deprecated and 
**will be removed** in version 2.0.

Example of migration from a model from 'Photon Generation' to 'Optics':

Before:
```yaml
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
```

After:
```yaml
pipeline:
  photon_collection:
# ^^^^^^^^^^^^^^^^^
#     modified
    - name: shot_noise
      func: pyxel.models.photon_collection.shot_noise
#           ~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^~~~~~~~~~~~
#                             modified
      enabled: true

    - name: optical_psf
      func: pyxel.models.photon_collection.optical_psf
#           ~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^~~~~~~~~~~~~
#                             modified
      enabled: true
      arguments:
        fov_arcsec: 5 # FOV in arcseconds
        pixelscale: 0.01 #arcsec/pixel
```

### Core
* Remove python37.
  (See [!594](https://gitlab.com/esa/pyxel/-/merge_requests/594)).

### Documentation
* Add Pyxel paper in documentation + Gitlab page.
  (See [!589](https://gitlab.com/esa/pyxel/-/merge_requests/589)).
* Added citation segment in README.md.
 (See [!591](https://gitlab.com/esa/pyxel/-/merge_requests/591)).
* Update FAQ.
 (See [!592](https://gitlab.com/esa/pyxel/-/merge_requests/592)
 and [!593](https://gitlab.com/esa/pyxel/-/merge_requests/593)).
* Add documentation about ModelGroup 'Photon Collection'.
  (See [!598](https://gitlab.com/esa/pyxel/-/merge_requests/598) and
  [!602](https://gitlab.com/esa/pyxel/-/merge_requests/602)).
* Add Pyxel to ASCL.net.
 (See [!603](https://gitlab.com/esa/pyxel/-/merge_requests/603)).
* Update contribution guide with steps for a merge request.
  (See [!607](https://gitlab.com/esa/pyxel/-/merge_requests/607)).
* Add more information in the contribution guide.
 (See [!606](https://gitlab.com/esa/pyxel/-/merge_requests/606)).

### Models
* Cannot reload a 'detector' from model 'pyxel.load_detector'.
  (See [!588](https://gitlab.com/esa/pyxel/-/merge_requests/588)).
* Move all models in ModelGroup 'Photon Generation and 'Optics' into a 
  new ModelGroup 'Photon Collection'. All models in 'Photon Generation' and 'Optics' are 
  obsolete/deprecated and will be removed in version 2.0.
  (See [!597](https://gitlab.com/esa/pyxel/-/merge_requests/597)).
* Add new ModelGroup 'Scene Generation'.
  (See [!600](https://gitlab.com/esa/pyxel/-/merge_requests/600)).
* Add new decorator 'deprecated' to deprecate old models.
  (See [!604](https://gitlab.com/esa/pyxel/-/merge_requests/604)).

### Others
* Remove `CCDCharacteristics`, `CMOSCharacteristics` and `MKIDCharacteristics`.
  (See [!590](https://gitlab.com/esa/pyxel/-/merge_requests/590)).
* Simplification when using 'group models' when generating a JSON Schema file.
  (See [!596](https://gitlab.com/esa/pyxel/-/merge_requests/596)).
* Create a 'tox' environment to check if the JSON schema is unchanged.
  (See [!601](https://gitlab.com/esa/pyxel/-/merge_requests/601)).
* Fix issues when running tests without having 'asdf' installed.
  (See [!605](https://gitlab.com/esa/pyxel/-/merge_requests/605)).



## 1.6.1 / 2023-01-09

This release brings a number of bugfixes and documentation improvements.

### Core
* Bug in data processing model group.
  (See [!585](https://gitlab.com/esa/pyxel/-/merge_requests/585)).

### Documentation
* Update documentation example.
  (See [!584](https://gitlab.com/esa/pyxel/-/merge_requests/584)).


## 1.6 / 2023-01-05

This release brings a number of bugfixes and documentation improvements.
A single release candidate (1.6rc0) was made to fix some issues.

The JSON Schema files for the 'stable' and 'latest' are respectively located in 
https://esa.gitlab.io/pyxel/pyxel_schema.json and https://esa.gitlab.io/pyxel/pyxel_schema_latest.json.
And detailed How-to guide about JSON Schema is available.

Add new models `load_detector` and `save_detector` for each Model Groups to load/inject or 
to save/extract a `Detector` object to/from a running pipeline.
Add new model group `data_processing` with a new model `statistics`.

### Core 
* Add 'Detector.load' and 'Detector.save'.
  (See [!559](https://gitlab.com/esa/pyxel/-/merge_requests/559)).
* Add method `Detector.to_xarray()`.
  (See [!563](https://gitlab.com/esa/pyxel/-/merge_requests/563)).
* Add parameter 'header' in function 'load_table'.
  (See [!565](https://gitlab.com/esa/pyxel/-/merge_requests/565)).
* Add new model group 'Data Processing'.
  (See [!566](https://gitlab.com/esa/pyxel/-/merge_requests/566)).
* Improve error message when validation an 'Observation' configuration.
  (See [!571](https://gitlab.com/esa/pyxel/-/merge_requests/571)).

### Documentation
* Add JSON Schema in the documentation.
  (See [!543](https://gitlab.com/esa/pyxel/-/merge_requests/543)).
* Fix issues sphinx.
  (See [!574](https://gitlab.com/esa/pyxel/-/merge_requests/574)).
* Add more documentation when installing from 'continuous_integration/environment.yml'.
  (See [!581](https://gitlab.com/esa/pyxel/-/merge_requests/581)).
* Correct image in Documentation.
  (See [!576](https://gitlab.com/esa/pyxel/-/merge_requests/576)).


### Models
* Add models `load_detector` and `save_detector` to load/save a detector from/to a file.
  (See [!545](https://gitlab.com/esa/pyxel/-/merge_requests/545)
  and [!562](https://gitlab.com/esa/pyxel/-/merge_requests/562)).
* Add option to current PRNU model.
  (See [!568](https://gitlab.com/esa/pyxel/-/merge_requests/568))

### Others
* Add unit tests to charge deposition in MCT model.
  (See [!553](https://gitlab.com/esa/pyxel/-/merge_requests/553)).
* Move JSON Schema files to https://esa.gitlab.io/pyxel
  (See [!555](https://gitlab.com/esa/pyxel/-/merge_requests/555)
  and [!556](https://gitlab.com/esa/pyxel/-/merge_requests/556)).
* Remove old Python 2.x type annotations.
  (See [!557](https://gitlab.com/esa/pyxel/-/merge_requests/557)).
* Fix issue when generating the JSON Schema file.
  (See [!558](https://gitlab.com/esa/pyxel/-/merge_requests/558)).
* Add a CI/CD pipeline to generate/check the JSON Schema file.
  (See [!535](https://gitlab.com/esa/pyxel/-/merge_requests/535)).
* Refactoring with 'refurb'.
  (See [!560](https://gitlab.com/esa/pyxel/-/merge_requests/560)).
* Use 'pyproject.toml'.
  (See [!530](https://gitlab.com/esa/pyxel/-/merge_requests/530)).
* Fix issue with unit test 'json schema'.
  (See [!569](https://gitlab.com/esa/pyxel/-/merge_requests/569)).
* Move 'environment.yml' in folder 'continuous_integration'.
  (See [!570](https://gitlab.com/esa/pyxel/-/merge_requests/570)).
* Enable 'License Compliance'.
  (See [!567](https://gitlab.com/esa/pyxel/-/merge_requests/567)).
* Add attrs as dependency.
  (See [!573](https://gitlab.com/esa/pyxel/-/merge_requests/573)).
* Create Wheel files in CI/CD.
  (See [!575](https://gitlab.com/esa/pyxel/-/merge_requests/575)).
* Pygmo error in calibration.
  (See [!580](https://gitlab.com/esa/pyxel/-/merge_requests/580)).

## 1.5 / 2022-11-21

This is a minor release that brings documentation improvements.

### Documentation
* Add more information about installation of 'poppy'.
  (See [!541](https://gitlab.com/esa/pyxel/-/merge_requests/541)).
* Add more information about 'wheel' file in the contribution guide.
  (See [!542](https://gitlab.com/esa/pyxel/-/merge_requests/542)).
* Add more installation documentation.
  (See [!547](https://gitlab.com/esa/pyxel/-/merge_requests/547)).

### Others
* The minimum version of 'holoview'
  (See [!540](https://gitlab.com/esa/pyxel/-/merge_requests/540)) was changed:

  | Package   | Old   | New        |
  | --------- |-------| ---------- |
  | holoviews | undef | **1.15**   |
* Create a new Conda Environment file to install 'pyxel' version 1.4.
  (See [!546](https://gitlab.com/esa/pyxel/-/merge_requests/546)
  and [!548](https://gitlab.com/esa/pyxel/-/merge_requests/548)).


## 1.4 / 2022-11-15

This release brings a number of bugfixes and documentation improvements.
A new 'charge_deposition_in_mct' model is added in the 'Charge Generation' group
and it's now possible to import/export a Detector object to/from an ASDF file.


### Core
* Implement multi-wavelength photon descriptions in `Detector.scene`.
  (See [!505](https://gitlab.com/esa/pyxel/-/merge_requests/505)).
* Implement a function that converts from `scopesim.Source` object to `Scene` object.
  (See [!506](https://gitlab.com/esa/pyxel/-/merge_requests/506)).
* Refactor and simplify `Calibration` and `Observation` classes.
  (See [!507](https://gitlab.com/esa/pyxel/-/merge_requests/507)
  and [!508](https://gitlab.com/esa/pyxel/-/merge_requests/508).
* Import/Export a Detector from/to an ASDF file.
  (See [!513](https://gitlab.com/esa/pyxel/-/merge_requests/513)).
* Identical argument names for different models crashes observation mode.
  (See [!524](https://gitlab.com/esa/pyxel/-/merge_requests/524)).
* Add methods '.plot()' and '.to_xarray' for 'Pixel', 'Photon', 'Signal', 'Image' and 'Phase'.
  (See [!528](https://gitlab.com/esa/pyxel/-/merge_requests/528)).

### Documentation
* Add a 'copy' button in documentation to copy code blocks.
  (See [!506](https://gitlab.com/esa/pyxel/-/merge_requests/506)).
* Fix typos in the documentation.
  (See [!517](https://gitlab.com/esa/pyxel/-/merge_requests/517)).
* Update doc for reading in files in exposure mode
  (See [!534](https://gitlab.com/esa/pyxel/-/merge_requests/534)).

### Models
* Create a simple cosmic ray model based on stopping power curves.
  (See [!339](https://gitlab.com/esa/pyxel/-/merge_requests/339)).
* Check correct range for dark_current.
  (See [!522](https://gitlab.com/esa/pyxel/-/merge_requests/522)).
* Add option for dark current non uniformity.
  (See [!425](https://gitlab.com/esa/pyxel/-/merge_requests/425)).

### Others
* Improved JSON Schema.
  (See [!509](https://gitlab.com/esa/pyxel/-/merge_requests/509)).
* Add more information in the output xarray.
  (See [!515](https://gitlab.com/esa/pyxel/-/merge_requests/515)).
* Remove decorator 'temporary_random_state'.
  (See [!519](https://gitlab.com/esa/pyxel/-/merge_requests/519)).
* Fix issue that runs two CI/CD pipeline.
  (See [!520](https://gitlab.com/esa/pyxel/-/merge_requests/520)).
* Enable creating a 'Calibration' configuration without installing pygmo.
  (See [!521](https://gitlab.com/esa/pyxel/-/merge_requests/521)).
* Add unit tests for 'Observation' mode.
  (See [!523](https://gitlab.com/esa/pyxel/-/merge_requests/523)).
* Fix bug in observation mode when using bad value.
  (See [!525](https://gitlab.com/esa/pyxel/-/merge_requests/525)).
* Remove used unit tests 'test_pyxel_loader'.
  (See [!531](https://gitlab.com/esa/pyxel/-/merge_requests/531)).
* 'JupyterLab' as an optional dependency of Pyxel.
  (See [!532](https://gitlab.com/esa/pyxel/-/merge_requests/532)).

## version 1.3.2 / 2022-09-08

This is a minor release to add a new reference about the latest SPIE paper.

### Documentation
* Add a reference to new paper from SPIE presented 
  at *SPIE Astronomical Telescopes & Instrumentation* conference.
  (See [!502](https://gitlab.com/esa/pyxel/-/merge_requests/502)).


## version 1.3.1 / 2022-09-07

This release is a bugfix to resolve issues with command `pyxel create-model`.

### Documentation
* Clarify full installation in the documentation.
  (See [!500](https://gitlab.com/esa/pyxel/-/merge_requests/500)).

### Others
* Command `pyxel create-model` is not working with Pyxel 1.3.
  (See [!499](https://gitlab.com/esa/pyxel/-/merge_requests/499)).


## version 1.3 / 2022-08-30

### Documentation
* Update documentation.
  (See [!412](https://gitlab.com/esa/pyxel/-/merge_requests/412)
  and [!496](https://gitlab.com/esa/pyxel/-/merge_requests/496)).

### Models
* Add physical models of non-linearity. Code provided by [Thibault Pichon](https://gitlab.com/tpichon).
  (See [!483](https://gitlab.com/esa/pyxel/-/merge_requests/483)).

### Others
* Exposed configuration.build_configuration to the developer API as a private function.  
  First contribution by [Kieran Leschinski](https://gitlab.com/kdleschinski).
  (See [!494](https://gitlab.com/esa/pyxel/-/merge_requests/494)).
* Function create model not working properly.
  (See [!495](https://gitlab.com/esa/pyxel/-/merge_requests/495)).


## version 1.2.1 / 2022-08-05

### Documentation.
* Fix issues with latest version of 'fsspec' (2022.7.1) and 'doc8' (1.0.0).
  (See [!491](https://gitlab.com/esa/pyxel/-/merge_requests/491)).


## version 1.2.0 / 2022-07-12

### Core
* Fix bug in 'ModelFitting.convert_to_parameters'.
  (See [!484](https://gitlab.com/esa/pyxel/-/merge_requests/484)).
* Implement new fitness function 'reduced_chi_squared'.
  (See [!485](https://gitlab.com/esa/pyxel/-/merge_requests/485)).
* In 'Archipelago', fix warnings with deprecated pandas function.
  Replace deprecated function `DataFrame.append` by `pandas.concat`.
  (See [!487](https://gitlab.com/esa/pyxel/-/merge_requests/487)).

### Documentation
* Add benchmarks in the documentation at this link 
  https://esa.gitlab.io/pyxel/benchmarks.
  (See [!486](https://gitlab.com/esa/pyxel/-/merge_requests/486)).
* Add more information about installation from 'conda' and 'pip'.
  (See [!488](https://gitlab.com/esa/pyxel/-/merge_requests/488)).

### Models

### Others
* The minimum versions of dependencies 'astropy', 'holoviews' and 'xarray' 
  (See [!481](https://gitlab.com/esa/pyxel/-/merge_requests/481)) were changed:

  | Package   | Old   | New        |
  | --------- |-------| ---------- |
  | astropy   | undef | **4.3**    |
  | holoviews | undef | **1.14.2** |
  | numpy     | 1.17  | **1.20**   |
  | xarray    | undef | **0.19**   |
* Speedup start-up time of Pyxel.
  (See [!482](https://gitlab.com/esa/pyxel/-/merge_requests/482)).


## version 1.1.2 / 2022-06-06

### Models
* Fix for: Charge generation model suppressing shot noise. 
  Solution from Gitter by [Lawrence Jones](https://gitlab.com/l_jones).
  (See [!475](https://gitlab.com/esa/pyxel/-/merge_requests/475)).
* Fix for: Redundant normalization in SAR ADC model.
  (See [!478](https://gitlab.com/esa/pyxel/-/merge_requests/478)).

### Others
* Provide multi-line string to 'pyxel.load.
  (See [!476](https://gitlab.com/esa/pyxel/-/merge_requests/476)).
* Fix issue with Mypy when using Numpy 1.22.
  (See [!477](https://gitlab.com/esa/pyxel/-/merge_requests/477)).

## version 1.1.1 / 2022-05-13

### Core

* Add fsspec >= 2021 compatibility.
  (See [!469](https://gitlab.com/esa/pyxel/-/merge_requests/469)).
* Implement parameters 'adc_voltage' and 'adc_bit_resolution' in 'Characteristics.to_dict'.
  (See [!470](https://gitlab.com/esa/pyxel/-/merge_requests/470)).

### Documentation
* Add new icon/badge 'I want to contribute !'
  (See [!727](https://gitlab.com/esa/pyxel/-/merge_requests/727)).


* Add how-to guide about saving/loading a Detector object.
  (See [!468](https://gitlab.com/esa/pyxel/-/merge_requests/468)).

### Models

* Add a temperature dependent dark current model.
  (See [!460](https://gitlab.com/esa/pyxel/-/merge_requests/460)).
* Add new model to simulate noise with SAR ADC.
  (See [!461](https://gitlab.com/esa/pyxel/-/merge_requests/461)).

### Others

* Fix issues found by 'mypy' version 0.950 and 'myst-nb' version 0.14.0.
  (See [!471](https://gitlab.com/esa/pyxel/-/merge_requests/471)).


## version 1.1.0 / 2022-04-22

### Core

* Remove maximum limit for attributes 'col' and 'row' in class ``Geometry``.
  The previous limit was set at a maximum of 10000 columns and 10000 rows.
  (See [!434](https://gitlab.com/esa/pyxel/-/merge_requests/434)).
* Replace deprecated appeding to dataframes with concatenating.
  (See [!444](https://gitlab.com/esa/pyxel/-/merge_requests/444)).
* Add an APD detector. Based on code from [James Gilbert](https://gitlab.com/labjg).
  (See [!449](https://gitlab.com/esa/pyxel/-/merge_requests/449)).
* Implement a property setter for the attribute times in class Readout.
  (See [!455](https://gitlab.com/esa/pyxel/-/merge_requests/455)).
* Convert a Detector (CCD, CMOS...) to a dictionary and vice versa.
  (See [!267](https://gitlab.com/esa/pyxel/-/merge_requests/267)).
* Implement methods `Detector.from_hdf5` and `Detector.to_hdf5`.
  (See [!448](https://gitlab.com/esa/pyxel/-/merge_requests/448)).
* Fix issues when saving/loading CMOS, APD and MKID Detector objects.
  (See [!463](https://gitlab.com/esa/pyxel/-/merge_requests/463)).

### Documentation

* Convert Changelog from Restructured Text to Markdown format.
  (See [!456](https://gitlab.com/esa/pyxel/-/merge_requests/456)).
* Write in documentation a list of available models for each detector type.
  (See [!457](https://gitlab.com/esa/pyxel/-/merge_requests/457)).

### Models

* Add a DC offset model. Based on code from [James Gilbert](https://gitlab.com/labjg).
  (See [!452](https://gitlab.com/esa/pyxel/-/merge_requests/452)).
* Add kTC reset noise model.
  (See [!451](https://gitlab.com/esa/pyxel/-/merge_requests/451)).
* Add an APD dark current model. Based on code from [James Gilbert](https://gitlab.com/labjg).
  (See [!453](https://gitlab.com/esa/pyxel/-/merge_requests/453)).
* Add an APD gain model.
  (See [!450](https://gitlab.com/esa/pyxel/-/merge_requests/450)).
* Add an APD readout noise model. Based on code from [James Gilbert](https://gitlab.com/labjg).
  (See [!454](https://gitlab.com/esa/pyxel/-/merge_requests/454)).
* Add a simple model that loads and applies PSF from a file.
  (See [!459](https://gitlab.com/esa/pyxel/-/merge_requests/459)).
* Fix models for usage in non-destructive mode.
  (See [!465](https://gitlab.com/esa/pyxel/-/merge_requests/465)).

### Others

* Updated ``poppy`` dependency to version 1.0.2. The previous version of ``poppy``
  are not compatible with ``astropy`` version 5.0.1.
  (See [!431](https://gitlab.com/esa/pyxel/-/merge_requests/431)).
* Fix an issue when building the documentation with Python 3.8.
  (See [!436](https://gitlab.com/esa/pyxel/-/merge_requests/436)).
* Create a static JSON Schema file.
  (See [!445](https://gitlab.com/esa/pyxel/-/merge_requests/445)
  and [!446](https://gitlab.com/esa/pyxel/-/merge_requests/446)).
* Bump pre-commit hook versions.
  (See [!447](https://gitlab.com/esa/pyxel/-/merge_requests/447)).


## version 1.0.0 / 2022-02-10

We are happy to announce that Pyxel has reached a stable version 1.0.0!
Pyxel releases will use [semantic versioning](https://semver.org/) notation.
Version 1.0 brings a simplified user experience, new models, 
parallel computing in observation mode, updated documentation, 
new examples, various bug fixes and much more. 
Excited for what comes next, stay tuned!

**Changes since last version:**

### Documentation

* Add pyxel brief history to documentation.
  (See [!429](https://gitlab.com/esa/pyxel/-/merge_requests/429)).


## version 1.0.0-rc.6 / 2022-02-09

### Others

* Update function display_persist.
  (See [!426](https://gitlab.com/esa/pyxel/-/merge_requests/426)).


## version 1.0.0-rc.5 / 2022-02-09

### Others

* Implement option to save outputs in common picture formats.
  (See [!416](https://gitlab.com/esa/pyxel/-/merge_requests/416)).
* Update MANIFEST.in.
  (See [!423](https://gitlab.com/esa/pyxel/-/merge_requests/423)).


## version 1.0.0-rc.4 / 2022-01-27

### Models

* Fix a bug when converting to photons in load_image.
  (See [!419](https://gitlab.com/esa/pyxel/-/merge_requests/419)).

### Others

* Pin astropy version due to a bug.
  (See [!420](https://gitlab.com/esa/pyxel/-/merge_requests/420)).


## version 1.0.0-rc.3 / 2022-01-26

### Core

* Improve digitization models and detector digitization characteristics.
  (See [!413](https://gitlab.com/esa/pyxel/-/merge_requests/413)).
* Remove default values from detector properties.
  (See [!415](https://gitlab.com/esa/pyxel/-/merge_requests/415)).

### Documentation

* Put labels to model API to know which data structures are models changing.
  (See [!405](https://gitlab.com/esa/pyxel/-/merge_requests/405)).
* Improved acronyms.
  (See [!414](https://gitlab.com/esa/pyxel/-/merge_requests/414)).

### Models

* Nghxrg model replacing pixel array instead of adding.
  (See [!404](https://gitlab.com/esa/pyxel/-/merge_requests/404)).
* Optimize persistence model.
  (See [!285](https://gitlab.com/esa/pyxel/-/merge_requests/285)).
* Fix for persistence model when using long time steps.
  (See [!407](https://gitlab.com/esa/pyxel/-/merge_requests/407)).
* Rename TARS to Cosmix.
  (See [!409](https://gitlab.com/esa/pyxel/-/merge_requests/409)).
* Add a simple ADC model.
  (See [!410](https://gitlab.com/esa/pyxel/-/merge_requests/410)).

### Others

* Fix mypy issues with new version of numpy 1.22.0.
  (See [!408](https://gitlab.com/esa/pyxel/-/merge_requests/408)).


## version 1.0.0-rc.2 / 2022-01-18

### Core

* Fix Characteristics validation checks.
  (See [!402](https://gitlab.com/esa/pyxel/-/merge_requests/402)).


## version 1.0.0-rc.1 / 2022-01-18

### Core

* Rename detector properties using whole words.
  (See [!292](https://gitlab.com/esa/pyxel/-/merge_requests/292)).
* Review classes Material and Environment.
  (See [!393](https://gitlab.com/esa/pyxel/-/merge_requests/393)).

### Documentation

* Add more documentation for CCDCharacteristics, CMOSCharacteristics, ....
  (See [!399](https://gitlab.com/esa/pyxel/-/merge_requests/399)).

### Others

* Small simplification. From [Albern S.](https://gitlab.com/abnsy).
  (See [!395](https://gitlab.com/esa/pyxel/-/merge_requests/395)).
* Updated ESA Copyright to 2022.
  (See [!396](https://gitlab.com/esa/pyxel/-/merge_requests/396)).
* Fix issue with licenses.
  (See [!397](https://gitlab.com/esa/pyxel/-/merge_requests/397)).
* Remove dead code.
  (See [!398](https://gitlab.com/esa/pyxel/-/merge_requests/398)).


## version 0.11.7 / 2022-01-07

### Documentation

* Fix broken links in the documentation.
  (See [!388](https://gitlab.com/esa/pyxel/-/merge_requests/388)).
* Fix links for 'suggest_edit' button in the documentation.
  (See [!389](https://gitlab.com/esa/pyxel/-/merge_requests/389)).
* Add better documentation for running modes..
  (See [!390](https://gitlab.com/esa/pyxel/-/merge_requests/390)).

### Models

* Refactoring of CDM model.
  (See [!375](https://gitlab.com/esa/pyxel/-/merge_requests/375)).

### Others

* Add netcdf4 to function show_versions.
  (See [!383](https://gitlab.com/esa/pyxel/-/merge_requests/383)).
* Fix issue with script 'download_last_environment_artifact.py'.
  (See [!386](https://gitlab.com/esa/pyxel/-/merge_requests/386)).


## version 0.11.6 / 2021-12-13

### Core

* Add new attribute 'Config.detector'.
  (See [!378](https://gitlab.com/esa/pyxel/-/merge_requests/378)).


### Documentation

* Split documentation into 'stable' and 'latest''.
  (See [!380](https://gitlab.com/esa/pyxel/-/merge_requests/380)).

### Others

* Include netcdf4 in dependencies.
  (See [!374](https://gitlab.com/esa/pyxel/-/merge_requests/374)).


## version 0.11.5 / 2021-12-07

### Core

* Fix an issue with calibration.
  (See [!353](https://gitlab.com/esa/pyxel/-/merge_requests/353)).
* Use an array in 'Charge' besides a dataframe.
  (See [!351](https://gitlab.com/esa/pyxel/-/merge_requests/351)).
* Move some general processing function into a common folder.
  (See [!359](https://gitlab.com/esa/pyxel/-/merge_requests/359)).
* Use detector.time_step in charge_generation models and allow floats in Charge arrays.
  (See [!365](https://gitlab.com/esa/pyxel/-/merge_requests/365)).

### Models

* Model 'nghxrg' is not working on Windows.
  (See [!361](https://gitlab.com/esa/pyxel/-/merge_requests/361)).
* Remove alignment model.
  (See [!364](https://gitlab.com/esa/pyxel/-/merge_requests/364)).
* Implement a non-linear FWC.
  (See [!338](https://gitlab.com/esa/pyxel/-/merge_requests/338)).
* Create a dark current model.
  (See [!310](https://gitlab.com/esa/pyxel/-/merge_requests/310)).


## version 0.11.4 / 2021-11-23

### Core

* Implement array-like data structures as numpy custom array containers.
  (See [!325](https://gitlab.com/esa/pyxel/-/merge_requests/325)).

### Documentation

* Add more internal links in the documentation.
  (See [!333](https://gitlab.com/esa/pyxel/-/merge_requests/333)).
* Move 'optical_psf' documentation to RST file.
  (See [!343](https://gitlab.com/esa/pyxel/-/merge_requests/343)).

### Models

* Move some models from 'readout_electronics' into separated files.
  (See [!323](https://gitlab.com/esa/pyxel/-/merge_requests/323)).
* Display model's name when running a pipeline.
  (See [!335](https://gitlab.com/esa/pyxel/-/merge_requests/335)).
* Add option to enable or disable progress bar in TARS model.
  (See [!337](https://gitlab.com/esa/pyxel/-/merge_requests/337)).

### Others

* Use 'deployment' in CI/CD.
  (See [!336](https://gitlab.com/esa/pyxel/-/merge_requests/336)).
* Fix an issue in CI/CD.
  (See [!340](https://gitlab.com/esa/pyxel/-/merge_requests/340)).
* Swap the environments name 'production' and 'development'.
  (See [!342](https://gitlab.com/esa/pyxel/-/merge_requests/342)).


## version 0.11.3 / 2021-11-15

### Core

* Multiply photon flux with detector time step in photon generation models.
  (See [!305](https://gitlab.com/esa/pyxel/-/merge_requests/305)).
* Initialize Photon class in detector reset function instead in models.
  (See [!309](https://gitlab.com/esa/pyxel/-/merge_requests/309)).
* Resolve "Use a 'with' statement to set a seed with 'numpy.random'.
  (See [!175](https://gitlab.com/esa/pyxel/-/merge_requests/175)).

### Others

* Remove some TODOs.
  (See [!288](https://gitlab.com/esa/pyxel/-/merge_requests/288)).


## version 0.11.2 / 2021-11-09

### Core

* Remove unnecessary warnings when Pygmo is not installed.
  (See [!286](https://gitlab.com/esa/pyxel/-/merge_requests/286)).
* Remove parallel computing with Numba.
  (See [!290](https://gitlab.com/esa/pyxel/-/merge_requests/290)).
* Use library 'click' to generate a Command Line Interface for script 'pyxel/run.py'.
  (See [!287](https://gitlab.com/esa/pyxel/-/merge_requests/287)).
* Simplify imports of sub packages.
  (See [!296](https://gitlab.com/esa/pyxel/-/merge_requests/296)).
* Fix an issue in imports.
  (See [!297](https://gitlab.com/esa/pyxel/-/merge_requests/297)).
* Re-enable dask for observation mode.
  (See [!172](https://gitlab.com/esa/pyxel/-/merge_requests/172)).

### Documentation

* Make pyxel compatible with Python 3.9.
  (See [!289](https://gitlab.com/esa/pyxel/-/merge_requests/289)).
* Update adding new models documentation with best practices.
  (See [!293](https://gitlab.com/esa/pyxel/-/merge_requests/293)).
* Add a 'Asking for help' chapter in the documentation.
  (See [!299](https://gitlab.com/esa/pyxel/-/merge_requests/299)).

### Others

* Fix issue with xarray 0.20.
  (See [!291](https://gitlab.com/esa/pyxel/-/merge_requests/291)).
* Updated black, isort and blackdoc in '.pre-commit.yaml'.
  (See [!294](https://gitlab.com/esa/pyxel/-/merge_requests/294)).
* Partially reduce Pyxel start-up time.
  (See [!302](https://gitlab.com/esa/pyxel/-/merge_requests/302)).


## version 0.11.1 / 2021-10-29

### Models

* Add a readout noise model for CMOS detectors.
  (See [!283](https://gitlab.com/esa/pyxel/-/merge_requests/283)).


## version 0.11 / 2021-10-27

### Core

* Output folder already existing when running 'load' two times.
  (See [!232](https://gitlab.com/esa/pyxel/-/merge_requests/232)).
* Implement normalisation for calibration mode.
  (See [!266](https://gitlab.com/esa/pyxel/-/merge_requests/266)).
* Refactor class `Charge`.
  (See [!271](https://gitlab.com/esa/pyxel/-/merge_requests/271)).
* Add new detector MKID. [Enrico Biancalani](https://gitlab.com/Dr_Bombero)
  (See [!206](https://gitlab.com/esa/pyxel/-/merge_requests/206)).
* Refactor single and dynamic mode into one named observation.
  (See [!263](https://gitlab.com/esa/pyxel/-/merge_requests/263)).
* Include observation mode functions in parametric mode.
  (See [!264](https://gitlab.com/esa/pyxel/-/merge_requests/264)).
* Include observation mode functions in calibration mode.
  (See [!265](https://gitlab.com/esa/pyxel/-/merge_requests/265)).
* Rename observation to exposure and parametric to observation.
  (See [!274](https://gitlab.com/esa/pyxel/-/merge_requests/274)).
* Improve the speed of function detector.reset.
  (See [!273](https://gitlab.com/esa/pyxel/-/merge_requests/273)).
* Optimize the speed of calibration in time-domain.
  (See [!276](https://gitlab.com/esa/pyxel/-/merge_requests/276)).

### Documentation

* Add more information about how-to release to Conda Forge.
  (See [!252](https://gitlab.com/esa/pyxel/-/merge_requests/252)).
* Update documentation on the refactored running modes.
  (See [!277](https://gitlab.com/esa/pyxel/-/merge_requests/277)).
* Update installation instructions for using pip and conda.
  (See [!279](https://gitlab.com/esa/pyxel/-/merge_requests/279)).
* Fix typos in installation instructions in documentation.
  (See [!280](https://gitlab.com/esa/pyxel/-/merge_requests/280)).

### Models

* Fix for consecutive photon generation models.
  (See [!193](https://gitlab.com/esa/pyxel/-/merge_requests/193)).
* Add model Arctic.
  (See [!229](https://gitlab.com/esa/pyxel/-/merge_requests/229)).
* Improve the speed of model 'charge_profile'.
  (See [!268](https://gitlab.com/esa/pyxel/-/merge_requests/268)).
* Simple conversion model not working with dark frames.
  (See [!281](https://gitlab.com/esa/pyxel/-/merge_requests/281)).

### Others

* Use tryceratops for try and except styling.
  (See [!255](https://gitlab.com/esa/pyxel/-/merge_requests/255)).
* Add a pipeline time profiling function.
  (See [!259](https://gitlab.com/esa/pyxel/-/merge_requests/259)).
* Add unit tests for model 'charge_profile'.
  (See [!269](https://gitlab.com/esa/pyxel/-/merge_requests/269)).
* Add unit tests for class 'Charge'.
  (See [!270](https://gitlab.com/esa/pyxel/-/merge_requests/270.)).
* Add unit tests for function 'calibration.util.check_range.
  (See [!278](https://gitlab.com/esa/pyxel/-/merge_requests/278.)).


## version 0.10.2 / 2021-09-02

### Core

* Enable logarithmic timing in dynamic mode.
  (See [!249](https://gitlab.com/esa/pyxel/-/merge_requests/249)).

### Others

* Fix issue with latest version of Mypy.
  (See [!253](https://gitlab.com/esa/pyxel/-/merge_requests/253)).


## version 0.10.1 / 2021-08-18

### Core

* Add more debugging information when Calibration mode fails.
  (See [!228](https://gitlab.com/esa/pyxel/-/merge_requests/228)).
* Add more debugging information in function 'get_obj_att'.
  (See [!243](https://gitlab.com/esa/pyxel/-/merge_requests/243)).
* Separate configuration loader from scripts in 'inputs_outputs'.
  (See [!250](https://gitlab.com/esa/pyxel/-/merge_requests/250)).

### Documentation

* Install a specific conda package version.
  (See [!235](https://gitlab.com/esa/pyxel/-/merge_requests/235)).

### Others

* Resolved calibration not allowing one column text files
  (See [!233](https://gitlab.com/esa/pyxel/-/merge_requests/233)).
* Update dependency to 'pygmo' from 2.11 to 2.16.1.
  (See [!234](https://gitlab.com/esa/pyxel/-/merge_requests/234)).
* Use mypy version 0.812.
  (See [!247](https://gitlab.com/esa/pyxel/-/merge_requests/247)).


## version 0.10 / 2021-06-13

### Core

* Add capability to save outputs of parametric mode as a xarray dataset.
  (See [!212](https://gitlab.com/esa/pyxel/-/merge_requests/212)).
* Add capability to save calibration result dataset to disk from YAML.
  (See [!214](https://gitlab.com/esa/pyxel/-/merge_requests/214)).
* Hide built-in Pyxel plotting capabilities (matplotlib figures from YAML).
  (See [!213](https://gitlab.com/esa/pyxel/-/merge_requests/213)).
* dynamic mode progress bar.
  (See [!219](https://gitlab.com/esa/pyxel/-/merge_requests/219)).
* Add capability to create models through command line using a template.
  (See [!217](https://gitlab.com/esa/pyxel/-/merge_requests/217)).
* Improved dynamic mode.
  (See [!229](https://gitlab.com/esa/pyxel/-/merge_requests/229)).
* Fix issue in creating parametric datasets.
  (See [!230](https://gitlab.com/esa/pyxel/-/merge_requests/230)).

### Documentation

* Update installation section.
  (See [!220](https://gitlab.com/esa/pyxel/-/merge_requests/220)).
* Update documentation on parametric and dynamic mode.
  (See [!228](https://gitlab.com/esa/pyxel/-/merge_requests/228)).

### Models

* Fix TARS model.
  (See [!227](https://gitlab.com/esa/pyxel/-/merge_requests/227)).
* Persistence model updated in charge_collection/persistence.py
  (See [!224](https://gitlab.com/esa/pyxel/-/merge_requests/224)).

### Others

* Fix circular import in parametric.py.
  (See [!216](https://gitlab.com/esa/pyxel/-/merge_requests/216)).
* Add compatibility to Mypy 0.900.
  (See [!223](https://gitlab.com/esa/pyxel/-/merge_requests/223)).


## version 0.9.1 / 2021-05-17

### Core

* Add missing packages when running 'pyxel.show_versions().
  (See [!193](https://gitlab.com/esa/pyxel/-/merge_requests/193)).
* Fix issues with 'fsspec' version 0.9.
  (See [!198](https://gitlab.com/esa/pyxel/-/merge_requests/198)).
* Refactoring class `Arguments.
  (See [!203](https://gitlab.com/esa/pyxel/-/merge_requests/203)).
* Add new detector MKID. [Enrico Biancalani](https://gitlab.com/Dr_Bombero)
  (See [!206](https://gitlab.com/esa/pyxel/-/merge_requests/206)).

### Others

* Fix issue when displaying current version.
  (See [!196](https://gitlab.com/esa/pyxel/-/merge_requests/196)).
* Cannot import sub-packages 'calibration' and 'models.optics'.
  (See [!189](https://gitlab.com/esa/pyxel/-/merge_requests/189)).
* Drop support for Python 3.6.
  (See [!199](https://gitlab.com/esa/pyxel/-/merge_requests/199)).
* Solve typing issues with numpy.
  (See [!200](https://gitlab.com/esa/pyxel/-/merge_requests/200)).
* Add functions to display calibration inputs and outputs in notebooks.
  (See [!194](https://gitlab.com/esa/pyxel/-/merge_requests/194)).
* Fix issue with the latest click version and pipeline 'license'.
  (See [!208](https://gitlab.com/esa/pyxel/-/merge_requests/208)).
* Resolve "Add 'LICENSE.txt' in MANIFEST.in".
  (See [!207](https://gitlab.com/esa/pyxel/-/merge_requests/207)).


## version 0.9 / 2021-03-25

### Core

* Fix a circular import in 'pyxel.data_structure'.
  (See [!171](https://gitlab.com/esa/pyxel/-/merge_requests/171)).
* Add ability to download Pyxel examples from command line.
  (See [!176](https://gitlab.com/esa/pyxel/-/merge_requests/176)).
* Add capability to read files from remote filesystems (e.g. http, ftp, ...).
  (See [!169](https://gitlab.com/esa/pyxel/-/merge_requests/169)).
* Add a mechanism to set option in Pyxel.
  (See [!170](https://gitlab.com/esa/pyxel/-/merge_requests/170)).
* Add capability to cache files in functions 'load_image' and 'load_data'.
  (See [!177](https://gitlab.com/esa/pyxel/-/merge_requests/177)).
* Add a stripe pattern illumination model.
  (See [!174](https://gitlab.com/esa/pyxel/-/merge_requests/174)).
* Add methods to display a Detector or an array of the Detector.
  (See [!173](https://gitlab.com/esa/pyxel/-/merge_requests/173)).
* Initiate Processor object inside running mode functions.
  (See [!184](https://gitlab.com/esa/pyxel/-/merge_requests/184)).
* Add HTML display methods for objects.
  (See [!185](https://gitlab.com/esa/pyxel/-/merge_requests/185)).
* Add ability to display input image in the display_detector function.
  (See [!186](https://gitlab.com/esa/pyxel/-/merge_requests/186)).
* Issue when creating islands in a Grid.
  (See [!188](https://gitlab.com/esa/pyxel/-/merge_requests/188)).

### Documentation

* Use the 'Documentation System'.
  (See [!178](https://gitlab.com/esa/pyxel/-/merge_requests/178)).
* Use the 'Documentation System'.
  (See [!181](https://gitlab.com/esa/pyxel/-/merge_requests/181)).
* Add an 'overview' page for each section in the documentation.
  (See [!183](https://gitlab.com/esa/pyxel/-/merge_requests/183)).

### Others

* Add a new badge for Binder.
  (See [!163](https://gitlab.com/esa/pyxel/-/merge_requests/163)).
* Fix issue when generating documentation in CI/CD.
  (See [!179](https://gitlab.com/esa/pyxel/-/merge_requests/179)).
* Always execute stage 'doc' in CI/CD.
  (See [!183](https://gitlab.com/esa/pyxel/-/merge_requests/183)).
* Pyxel version cannot be retrieved.
  (See [!189](https://gitlab.com/esa/pyxel/-/merge_requests/189)).
* Remove pyviz from dependencies.
  (See [!191](https://gitlab.com/esa/pyxel/-/merge_requests/191)).

### Pipelines

* Calibration - Export champions for every evolution and every island.
  (See [!164](https://gitlab.com/esa/pyxel/-/merge_requests/164)).
* Calibration - Extract best individuals.
  (See [!165](https://gitlab.com/esa/pyxel/-/merge_requests/165)).
* Calibration - Fix an issue when extracting parameters.
  (See [!166](https://gitlab.com/esa/pyxel/-/merge_requests/166)).


## version 0.8.1 / 2021-01-26

### Documentation

* Enabled sphinxcontrib-bibtex version 2.
  (See [#155](https://gitlab.com/esa/pyxel/-/issues/155)).

### Others

* Add a new badge for Google Group.
  (See [!157](https://gitlab.com/esa/pyxel/-/merge_requests/157)).
* Prepare Pyxel to be uploadable on PyPI.
  (See [!161](https://gitlab.com/esa/pyxel/-/merge_requests/161)).


## version 0.8 / 2020-12-11

### Core

* Improved user friendliness.
  (See [#144](<https://gitlab.com/esa/pyxel/issues/144>)).
* Simplified the look of YAML configuration files.
  (See [#118](<https://gitlab.com/esa/pyxel/issues/118>)).
* Extracted functions to run modes separately from pyxel.run.run()
  (See [#61](<https://gitlab.com/esa/pyxel/issues/61>)).
* Refactored YAML loader, returns a class Configuration instead of a dictionary.
  (See [#60](<https://gitlab.com/esa/pyxel/issues/60>)).
* Created new classes Single and Dynamic to store running mode parameters.
  (See [#121](<https://gitlab.com/esa/pyxel/issues/121>)).
* Split class Outputs for different modes and moved to inputs_ouputs.
  (See [#149](<https://gitlab.com/esa/pyxel/issues/149>)).
* Added a simple Inter Pixel Capacitance model for CMOS detectors.
  (See [#65](<https://gitlab.com/esa/pyxel/issues/65>)).
* Added a model for the amplifier crosstalk.
  (See [#116](<https://gitlab.com/esa/pyxel/issues/116>)).
* Added ability to load custom QE maps.
  (See [#117](<https://gitlab.com/esa/pyxel/issues/117>)).
* Use 'Dask' for Calibration mode.
  (See [!145](https://gitlab.com/esa/pyxel/-/merge_requests/145)).

### Others

* Change licence to MIT.
  (See [!142](https://gitlab.com/esa/pyxel/-/merge_requests/142)).
* Change Pyxel's package name to 'pyxel-sim'.
  (See [!144](https://gitlab.com/esa/pyxel/-/merge_requests/114)).
* Added a 'How to release' guide.
  (See [#109](<https://gitlab.com/esa/pyxel/issues/109>)).
* Remove_folder_examples_data.
  (See [!148](https://gitlab.com/esa/pyxel/-/merge_requests/148)).
* Fix typo in documentation.
  (See [!149](https://gitlab.com/esa/pyxel/-/merge_requests/149)).
* Updated documentation according to v0.8.
  (See [!153](https://gitlab.com/esa/pyxel/-/merge_requests/153)).


## version 0.7 / 2020-10-22

### Core

* Update .gitignore file.
  (See [!123](https://gitlab.com/esa/pyxel/-/merge_requests/123)).
* Added capability to load more image formats and tests.
  (See [!113](https://gitlab.com/esa/pyxel/-/merge_requests/113)).
* Create a function 'pyxel.show_versions().
  (See [!114](https://gitlab.com/esa/pyxel/-/merge_requests/114)).
* Shorter path to import/reference the models.
  (See [!126](https://gitlab.com/esa/pyxel/-/merge_requests/126)).
* Remove deprecated methods from Photon class.
  (See [!119](https://gitlab.com/esa/pyxel/-/merge_requests/119)).
* Instances of 'DetectionPipeline' are not serializable.
  (See [!120](https://gitlab.com/esa/pyxel/-/merge_requests/120)).
* Cannot run 'calibration' pipeline with multiprocessing or ipyparallel islands.
  (See [!121](https://gitlab.com/esa/pyxel/-/merge_requests/121)).
* Make package and script 'pyxel' executable.
  (See [!112](https://gitlab.com/esa/pyxel/-/merge_requests/112)).
* Created a function inputs_outputs.load_table().
  (See [!132](https://gitlab.com/esa/pyxel/-/merge_requests/132)).
* Reimplement convolution in POPPY optical_psf model.
  (See [#52](<https://gitlab.com/esa/pyxel/issues/52>)).
* Add property 'Detector.numbytes' and/or method 'Detector.memory_usage()'
  (See [!116](https://gitlab.com/esa/pyxel/-/merge_requests/116)).
* Created jupyxel.py for jupyter notebook visualization.
  (See [!122](https://gitlab.com/esa/pyxel/-/merge_requests/122)).

### Documentation

* Remove comments for magic methods.
  (See [!127](https://gitlab.com/esa/pyxel/-/merge_requests/127)).


## version 0.6 / 2020-09-16

* Improved contributing guide
  (See [#68](<https://gitlab.com/esa/pyxel/issues/68>)).
* Remove file '.gitlab-ci-doc.yml'
  (See [#73](<https://gitlab.com/esa/pyxel/issues/73>)).
* Change license and add copyrights to all source files.
  (See [#69](<https://gitlab.com/esa/pyxel/issues/69>)).
* Fix issues with example file 'examples/calibration_CDM_beta.yaml'.
  (See [#75](<https://gitlab.com/esa/pyxel/issues/75>)).
* Fix issues with example file 'examples/calibration_CDM_irrad.yaml'.
  (See [#76](<https://gitlab.com/esa/pyxel/issues/76>)).
* Updated Jupyter notebooks examples.
  (See [#87](<https://gitlab.com/esa/pyxel/issues/87>)).
* Apply command 'isort' to the code base.
* Refactor class `ParametricPlotArgs`.
  (See [#77](<https://gitlab.com/esa/pyxel/issues/77>)).
* Create class `SinglePlot`.
  (See [#78](<https://gitlab.com/esa/pyxel/issues/78>)).
* Create class `CalibrationPlot`.
  (See [#79](<https://gitlab.com/esa/pyxel/issues/79>)).
* Create class `ParametricPlot`.
  (See [#80](<https://gitlab.com/esa/pyxel/issues/80>)).
* Add templates for bug report, feature request and merge request.
  (See [#105](<https://gitlab.com/esa/pyxel/issues/105>)).
* Parallel computing for 'parametric' mode.
  (See [#111](<https://gitlab.com/esa/pyxel/issues/111>)).
* Improved docker image.
  (See [#96](<https://gitlab.com/esa/pyxel/issues/96>)).
* Fix calibration pipeline.
  (See [#113](<https://gitlab.com/esa/pyxel/issues/113>)).
* CI/CD pipeline 'licenses-latests' fails.
  (See [#125](<https://gitlab.com/esa/pyxel/issues/125>)).


## version 0.5 / 2019-12-20

* Clean-up code.
* Remove any dependencies to esapy_config
  (See [#54](<https://gitlab.com/esa/pyxel/issues/54>)).
* Refactor charge generation models to avoid code duplication
  (See [#49](<https://gitlab.com/esa/pyxel/issues/49>)).
* Implement multi-threaded/multi-processing mode
  (See [#44](<https://gitlab.com/esa/pyxel/issues/44>)).


## version 0.4 / 2019-07-09

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

## version 0.3 / 2018-03-26

* Single and Parametric mode have been implemented
* Infrastructure code has been placed in 2 new projects: esapy_config and esapy_web
* Web interface (GUI) is dynamically generated based on attrs definitions
* NGHxRG noise generator model has been added

## version 0.2 / 2018-01-18

* TARS cosmic ray model has been reimplemented and added

## version 0.1 / 2018-01-10

* Prototype: first pipeline for a CCD detector
