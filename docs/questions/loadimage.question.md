---
title: Is there a way to add photons to a Detector directly from a file containing photons or pixel instead of converting from image in ADU to photons via the PTF?
---
Yes, with the model 'load_image' in the photon generation model group it is possible to load photons directly from a file.
You can set the argument 'convert_to_photons' to false, and it will use your input array without converting it via PTF.
See [here](https://esa.gitlab.io/pyxel/doc/stable/references/model_groups/photon_collection_models.html#load-image) for more details.