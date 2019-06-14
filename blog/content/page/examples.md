---
title: Examples
subtitle: 
comments: false
---

# Parametric Analysis mode

- Runs the pipeline multiple times changing a set of model and/or instrument parameters (e.g. in a range)
- Processing: sequential, embedded, parallel (from file)
- Use case: sensitivity analysis, image batch generation

# Calibration (optimization) mode

- Runs the evolution of pipeline calibrating a set of model and/or instrument parameters based on target datasets, finding the global (or local) minimum of the (user-defined) fitness function
- Algorithms: Simple Genetic, Self-Adaptive Differential Evolution, Non-Linear Optimization
- Use case: fitting model to target data, optimization of instrument attributes

