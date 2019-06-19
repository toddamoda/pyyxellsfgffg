---
title: Models
subtitle: 
comments: false
---

# Models in Pyxel

This is not an exhaustive list of Pyxel models!
 
## POPPY

POPPY (Physical Optics Propagation in PYthon)[^1] simulates physical optical propagation including diffraction. 
It implements a flexible framework for modeling Fraunhofer and Fresnel diffraction and point spread function formation, 
particularly in the context of astronomical telescopes.

* Developed by: Marshall Perrin et al., STScI
* Developed for: James Webb Space Telescope
* https://poppy-optics.readthedocs.io/en/stable

<center>
{{< figure src="/img/poppy.png" caption="POPPY (Physical Optics Propagation in PYthon), Credit: STScI" >}}
</center>

## CosmiX

CosmiX[^2] simulates charge deposition by cosmic rays. It is still under development.

* Developed by: David Lucsanyi, ESA
* Developed for: general

<center>
{{< figure src="/img/cosmix.png" caption="CosmiX cosmic ray model" width="600px" >}}
</center>

## CDM 

CDM (Charge Distortion Model)[^3] simulates Charge Transfer Inefficiency in radiation damaged CCD detectors.

* Developed by: Alexander Short, ESA
* Developed for: Gaia mission

<center>
{{< figure src="/img/cdm.png" caption="CDM (Charge Distortion Model)" width="500px" >}}
</center>

## ngHxRG 

HxRG Noise Generator[^4] simulates readout noises specifically for HxRG type hybrid HgCdTe detectors.

* Developed by: Bernard J. Rauscher, NASA
* Developed for: James Webb Space Telescope

<center>
{{< figure src="/img/nghxrg.png" caption="ngHxRG Noise Generator" >}}
</center>

# Models to be added...

* arctic (Algorithm foR CTI Correction)
  * https://github.com/ocordes/arctic
* GalSim (modular galaxy image simulation toolkit)
  * https://github.com/GalSim-developers/GalSim
* Allpix<sup>2</sup> (pixel detector simulation framework)
  * https://project-allpix-squared.web.cern.ch


[^1]: M. D. Perrin et al.: *"Simulating point spread functions for the James Webb Space Telescope with WebbPSF"*, Space Telescopes and Instrumentation 2012, SPIE Proc., Vol. 8442, pp. 11. (2012).
[^2]: D. Lucsanyi, T. Prod'homme: *"Simulating charge deposition by cosmic rays inside astronomical imaging detectors"*, Session E: Photonics, Optoelectronics & Sensors, RADECS conference 2019.
[^3]: A. Short et al.: *"An analytical model of radiation-induced Charge Transfer Inefficiency for CCD detectors"*, Monthly Notices of the Royal Astronomical Society 430(4), 3078{3085 (2013).
[^4]: B. J. Rauscher: *"Teledyne H1RG, H2RG, and H4RG Noise Generator"*, Publications of the Astronomical Society of the Pacific 127(957), 1144 (2015).    
