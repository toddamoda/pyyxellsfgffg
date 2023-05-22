---
title: Is there any way to use Pyxel to produce a bias or dark image without including any image file?
---

Without the models in the pipeline, Pyxel will still run, but will generate nothing, so just zero arrays. 
Dark image for example would be generated using a dark current model in charge_generation. 
The detector object stores the data and some properties that are needed by more than one model, 
but it doesn't directly influence how the stored data is edited, this information is in the pipeline.