PYXEL a detector simulation framework
=====================================

tbd


Requirements
------------

- ``python >= 3.5``


Build and Test Commands
-----------------------

Install this package::

    pip install pyxel --extra-index-url http://lab-linux-server.estec.esa.int/pypiserver --trusted-host lab-linux-server.estec.esa.int
    
Install build and test tools::

    pip install docutils
    pip install coverage
    pip install pylint
    pip install nose
    pip install tox
    pip install plantuml

From the root directory (rpc) run the following commands::

    pylint --rcfile=pylint.cfg pyxel
    nosetests --with-coverage --cover-erase --cover-html
    coverage run -m unittest discover -b -v -s .
    coverage report
    python -m unittest discover
    python setup.py bdist_wheel

To build the README.rst documentation::

    pygmentize -S default -f html -a .python > style.css
    python %VIRTUAL_ENV%/Scripts/rst2html.py --link-stylesheet --cloak-email-addresses --toc-top-backlinks --syntax-highlight=short --stylesheet-dirs=. --stylesheet README.css README.rst readme.html

Syntax highlighting using pygments: http://pygments.org/docs/cmdline/

PyPI Register / Upload commands::

    python setup.py bdist_wheel
    # For PyPI LIVE use: https://pypi.python.org/pypi
    python setup.py register -r https://testpypi.python.org/pypi
    # For PyPI LIVE use: pypi
    python setup.py bdist_wheel upload -r pypitest
    # or,
    python setup.py bdist_wheel upload -r http://lab-linux-server.estec.esa.int:9999
    
To authenticate automatically create a file named *.pypirc* in your $HOME directory,::

	[distutils]
	index-servers =
	    sci-fv
	
	[sci-fv]
	repository: http://lab-linux-server.estec.esa.int/packages
	username: lab
	password: <password>
	
Now the upload command can be executed without an authentication prompt using,::

	python setup.py bdist_wheel upload -r sci-fv

If the above has 
	

Make sure the `.pypirc` file is defined in your home folder before running
the above commands.


Documentation
-------------

The documentation of **Pyxel** can be found at this link: http://sci-fv.io.esa.int/pyxel/doc


License
-------

ESA Software Community License - Type 3. See License File.
