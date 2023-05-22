---
title: Is there a simple example of a configuration file?
alt_titles:
  - "What inputs are definitely required to be in the yaml file?"
  - "What are the minimal requirements in a yaml file that it does not result in a blank image?"
---

There are a couple of models that are required in the pipeline to get an image in the end.  
One has to make use of simple models in the pipeline that the conversion **photon->charge->pixel->signal->image** is happening.

A simple pipeline example of a configuration yaml file in exposure mode can be found here: 
[simple_exposure.yaml](https://gitlab.com/esa/pyxel-data/-/blob/master/examples/exposure/simple_exposure.yaml).