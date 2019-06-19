---
title: How it works
subtitle: 
comments: false
---

# Imitating the real detectors

With Pyxel, we are imitating the working principles of the imaging photon detectors following 
the steps of visible and infrared photon detection in case of both CCD and CMOS-based detectors.

<center>
{{< figure src="/img/beletic-detector-diagram.png" caption="Steps of photon detection, Credit: James W. Beletic (2009)" width="500px" >}}
</center>

## Detection Pipeline

The core algorithm of Pyxel, hosting and running the models sequentially. The models are grouped into 
different model groups based on the working principles of a real instrument from photon propagation to image processing.

## Detector object

A bucket containing all properties and data of the simulated instrument, which is passed to 
all the models activated by the user, and may be used or modified by them as well.   

<center>
{{< figure src="/img/pipeline-and-detector.png" caption="Detection Pipeline and Detector object of Pyxel" width="600px" >}}
</center>


[^1]: James W. Beletic: *Imaging Sensor Technologies for Astronomy, Planetary Exploration & Earth Observation*, March 10, 2009.
