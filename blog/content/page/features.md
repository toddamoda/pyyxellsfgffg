---
title: Features
subtitle: 
comments: false
---

# Parametric Analysis

- Runs the pipeline multiple times changing a set of model and/or instrument parameters (e.g. in a range)
- Use case: sensitivity analysis, image batch generation

<img src="/img/ptc.png" width="500px" alt="Photon Transfer Curve with Parametric Analysis mode">


# Calibration (optimization)

- Runs the evolution of pipeline calibrating a set of model and/or instrument parameters based 
on target datasets, finding the global (or local) minimum of the (user-defined) fitness function
- Algorithms: Simple Genetic, Self-Adaptive Differential Evolution, Non-Linear Optimization
- Use case: fitting model to target data, optimization of instrument attributes

<img src="/img/cdm_fitting.png" width="500px" alt="Final population of model parameters fitted to target data">
