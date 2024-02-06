=============
Brief history
=============

Pyxel was born in 2017, when a team of physicists,
detector experts and software engineers from ESA's Science payload validation section
decided to develop a python-based detector simulation framework
capable of hosting and pipelining any detector effects model.

ESA's Science payload validation section hosts a laboratory for detector characterisation.
The laboratory is used to determine the performance of detectors in a representative environment
(temperature, operating point, radiation),
validate the performance results obtained in other facilities (laboratories, companies),
and carry out very specific experimental tests tailored to mission needs.

The interpretation of test results as well as
the transfer of knowledge from lab to mission performance very often requires modelling and simulations.
Several detector effects models were born that way.
With soon the realisation that similar models had already been developed by the community and sometimes even at ESA.
At the same time, python became more and more popular among the lab team members for EGSE development,
data processing and analysis.
The idea of developing a framework - some sort of python package -
that could host and pipeline existing models from different contributors was born.

After several brainstorming sessions for a first conceptual architecture,
the Pyxel team organised a survey internal to ESA among potential users
(detector specialists, instrument and payload system engineers, optical engineers, etc.).
From the survey a first set of requirements were derived.
The positive feedback received fuelled our motivation to develop Pyxel
and a prototype was already on the table by June 2018 when it was presented at
the SPIE astronomical telescopes and instrumentation conference in Austin, Texas.

In 2019, we released a beta version and welcomed beta testers on gitlab.
At that time members of the European Southern Observatory detector group as well as
several other members from the larger astronomy instrumentation community joined the Pyxel collaboration
and helped us developing the tool further towards v1.0.

Since 2020 the tool is capable of simulating :term:`CCD`, :term:`CIS`, Hybridised :term:`MCT`
detectors and :term:`MKID` detectors and operate in several modes including a model calibration mode
which can make use of laboratory test data to extract model parameters.

2021 has been a key year in the development of Pyxel towards v1.0,
with close to a hundred gitlab users, the public release of Pyxel under the permissive MIT license,
and the release of tutorials explaining Pyxel's ins and outs: how to install it, how to use it,
how to add a model etc.
2021 culminated with the organisation of a detector modelling workshop DeMo 2021
gathering several hundreds of detector and instrument simulation enthusiasts from the instrumentation community,
and demonstrating the potential of such a tool to foster knowledge transfer.

In 2024, we achieved version 2.0, enhancing Pyxel's functionality to be multi-wavelength compatible.
This was achieved through the implementation of a scene generation model group, enabling the
creation of scenes in the sky, and the adaptation of models to effectively handle and process
wavelength information.

Pyxel is steadily growing with new features, application domains, and users.
The focus remains on adding new validated models, simplifying the architecture,
and improving the user experience.
