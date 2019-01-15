.. _new_model:

Adding new models
===================

:ref:`Models <models>`

Users and developers can easily add any kind of new or already existing
model to Pyxel, thanks to the model plug-in mechanism developed for this
purpose.

Pyxel decorators
------------------



Model wrappers
----------------

If your model is a Python class, package or it is implemented in a
programming language other than Python (C/C++, Fortran, Java),
then it is necessary to create a wrapper model function,
which calls and handles the original code (class, package or
non-Python code).
