# pywrapfst

Fork of the official [OpenFst python wrapper](http://www.openfst.org/twiki/bin/view/FST/PythonExtension)

# Requirements

In order to install **pywrapfst** the following tools are required:

* [Python](https://www.python.org/) 3.0 or greater (tested on 3.5)
* [Cython](http://cython.org)
* [OpenFst](http://www.openfst.org/twiki/bin/view/FST/WebHome) version 1.6.5 (others might work too but were not tested)
installed with the *far* extension. When installing OpenFst, do NOT
install the *python* extension !

Though not required, we strongly recommend the use of the
[Anaconda](https://docs.anaconda.com/anaconda/) python distribution as
it grealty simplifies depedencies.

# Installation

In **pywrapfst** root directory run:

    $ python setup.py install

If OpenFst was installed in a non-standard location, set appropriately
the environment variable `LD_LIBRARY_PATH` as in the following example:

    $ LD_LIBRARY_PATH=/path/to/my/library/directory python setup.py install

You can check if the installation was successful by running:

    $ python -c "import pywrapfst; print('ok')"

# Usage


