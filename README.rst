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

    $ python3 -m venv ./env

#. Install the latest version in full with pip::

    $ ./env/bin/pip install '.[audio]'
    $ ./env/bin/python setup.py install

.. _Korg Volca Sample library: http://korginc.github.io/volcasample/index.html
.. _Volca Factory Sample set: http://www.korg.com/us/support/download/software/0/370/1476/




Building Syro CLI only
======================

    $ ./build_syro_cli.sh


Using Syro CLI only
======================

!! only 16bit mono wav samples are supported !!

#. To convert it::

   $ ffmpeg -i original_sample.wav -acodec pcm_s16le -ac 1 -ar 16000 out.wav

Usage examples:

#. Sample(Compress bit=16), number = 81, file = test2/81/m81_202109.wav::

    $ ./syro_build/syro test_output_sample81.wav 's81c:test2/81/m81_202109.wav'

#. Sample erase, number = 135::

    $ ./syro_build/syro test_output_erase_135.wav 'e135:'

#. Sample(Compress bit=12), number = 181, file = test2/81/m81_202109.wav::

    $ ./syro_build/syro test_output_sample181.wav 's181c12:test2/81/m81_202109.wav'

See `readme_en.markdown -> ####SourceFile` for more.
