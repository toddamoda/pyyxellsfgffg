.. _install:

Installation
==============

..
   **pyxel** is available on our own ``PyPI server`` at the following
   url: `<http://lab-linux-server.estec.esa.int/pyxel/>`.
   By using this server, you are sure to have the latest stable version.

   To install, simply use ``pip``:

   .. code-block:: python

      pip install pyxel
      pip install --index-url=http://lab-linux-server.estec.esa.int/pypi/simple \
      ...         --extra-index-url=http://lab-linux-server.estec.esa.int/pypi/simple \
      ...         --trusted-host=lab-linux-server.estec.esa.int \
      ...         pyxel

   To upgrade pyxel to the latest version:

   .. code-block:: python

      pip install --upgrade pyxel
