..  Titling
    ##++::==~~--''``

Volcasample
:::::::::::

This is a Python wrapping of the `Korg Volca Sample library`_.

.. caution:: You risk data loss.

   This software will delete the factory defaults from your Volca Sample.

   Please make sure you know how to restore the `Volca Factory Sample set`_
   before you run the program.

Features
========

* Wraps the public interface of the Korg Volca Library so you can call
  it from your Python code.
* Creates and maintains project spaces so you can store and rate your
  samples.
* Provides a neat command line interface (CLI) for writing a set of
  samples to your Volca.

Installation
============

The installation process builds the Korg source code which is included
in this package. Therefore the `gcc` build tools must be present.

Installation has been tested on Ubuntu 16.04 and MacOSX 10.11.

#. Create a virtual environment for volcasample::

    $ python3 -m venv ~/py3-vs

#. Install the latest version in full with pip::

    $ ~/py3-vs/bin/pip install volcasample[audio]

.. _Korg Volca Sample library: http://korginc.github.io/volcasample/index.html
.. _Volca Factory Sample set: http://www.korg.com/us/support/download/software/0/370/1476/
