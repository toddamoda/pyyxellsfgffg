---
title: Features
subtitle: 
comments: false
---

# Parametric Analysis

- Runs the Detection Pipeline multiple times changing a set of model and/or instrument parameters 
- Varying parameters can be defined using a list, range or NumPy functions
- **Algorithms** (in case multiple parameters): Serial (Sequential or Embedded), Parallel
- **Use cases:** Sensitivity analysis, Image batch generation
- **Example:** CCD Photon Transfer Curve generated and plotted using different simple noise models

<center>
{{< figure src="/img/ptc.png" caption="Photon Transfer Curve with Parametric Analysis mode" width="500px" >}}
</center>

# Calibration, Optimization

- Runs the evolution of the Detection Pipeline calibrating a set of model and/or instrument parameters 
based on target dataset(s), finding the (global or local) minimum of the fitness function
- **Algorithms:** Simple Genetic Algorithm, Self-Adaptive Differential Evolution, Non-Linear Optimization (NLopt) Algorithms
- **Fitness functions:** User-defined function, Sum of squared residuals, Sum of absolute deviations, etc.  
- **Use cases:** Fitting models to target data, Optimization of instrument attributes
- **Exmaple:** Finding the density and release time of charge traps of a Charge Transfer Inefficiency model 

<center>
{{< figure src="/img/cdm_fitting.png" caption="Final population of model parameters fitted to target measurement data using an evolutionary algorithm" width="500px" >}}
</center>

# Dynamic, Time-dependent Readout

- Runs the Detection Pipeline for multiple time steps modelling that the time is elapsing
- This mode allows to read out the CMOS-based detector non-destructively in specific time steps
- Can be also used to run time-dependent models (e.g. persistence) relying on the history of 
detector object or flux of incident photons 
- **Use cases:** Running time-dependent models, Non-destructive readout 
- **Exmaple:** Persistence model, Dark Current model, Fowler-N sampling, Up-The-Ramp sampling

<center>
{{< figure src="/img/fowler-n-sampling.png" caption="Fowler-N sampling of CMOS sensor signal" width="400px" >}}
</center>


# User-friendly configuration file

- Pyxel needs only one YAML configuration file as an input
- Structured, easy-to-read and understand
- 3 main parts: `simulation`, `detector`, `pipeline`  

<center>
{{< figure src="/img/yaml.png" caption="Structured YAML configuration file of Pyxel" width="400px" >}}
</center>

# Graphical User Interface 

- Web-based GUI (html), which can displayed and used via a web browser 
- The GUI is automatically generated based on the Pyxel YAML configuration file
- **Under development, but coming soon!**

<center>
{{< figure src="/img/pyxel-gui.png" caption="Web-based Graphical User Interface of Pyxel" width="600px" >}}
</center>