---
title: Why do I retrieve a blank image but no error?
alt_titles:
  - "What inputs are definitely required to be in the yaml file?"
  - "What are the minimal requirements in a yaml file that it does not result in a blank image?"
---

There are a couple of models that are required in the pipeline to get an image in the end.  
One have to make use of simple models in the pipeline that the conversion **photon->charge->pixel->signal->image** is happening.

Example: 
If you have only the model `load_image` in your pipeline and make use of the function `pyxel.display_detector(detector)`
you will retrieve the plot with photon, but the plots showing pixel or image are blank, because no conversion is taking place in the pipeline.

A simple pipeline example of a configuration yaml file in exposure mode can be found here: 
[simple_exposure.yaml](https://gitlab.com/esa/pyxel-data/-/blob/master/examples/exposure/simple_exposure.yaml).