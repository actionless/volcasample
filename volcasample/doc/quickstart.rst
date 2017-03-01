..  Titling
    ##++::==~~--''``
    
Quickstart Guide
================

Create a project for your samples
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

There are 100 sample slots on your Volca. A `project` is a directory
with 100 more inside it. You create this structure like so::

    $ ~/py3-vs/bin/volcasample project --new

    Creating project tree at ~/volcasamples

    .......................................................... OK.

You'll see that the ``volcasamples`` directory contains others named
``00``, ``01``, and so on up to ``99``.

Populate the project with your sound files
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Place into each numbered directory a maximum of one audio file.
You can record samples yourself, or take them from disks or sites
online.

They must be in uncompressed PCM `.wav` format. Data should be 16 or
24 bit, sampled at a rate of 44.1 or 48KHz.

Check how big those files are
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The Volca Sample allows only 40MB of audio and a maximum of 65s total
playback time. So it's likely not every file in your project will fit
at once.

Use the program to `audition` your project. First, we'll get a report
on the relative sizes of those samples::

    $ ~/py3-vs/bin/volcasample audition --silent

    Auditioning project at ~/volcasamples

    0000000000111111111122.....6666666666777777777788888888889999999999
    0123456789012345678901.....0123456789012345678901234567890123456789
    .::.:::.:..:     :    .....       :Iiiii:iIIiiiiiiiIiiiIiiiiiiiiiii

The output is truncated here. The program outputs a symbol for each of
the 100 samples in the project. The symbols are as follows:

======  ======  =======================================================
Symbol  Size    Sound
======  ======  =======================================================
space   Zero    There is no audio in this slot
.       Tiny    The audio is momentary
:       Small   The audio is a short tone or reverberation
i       Medium  The audio has some length, like a repeated beat
I       Large   A lengthy sample
#       Full    A sample so big it cannot fit the Volca even on its own
======  ======  =======================================================

The three lines of output will be the basis of how we define the subset
of samples to be sent to the Volca. So let's save it to a file for
later::

    $ ~/py3-vs/bin/volcasample audition --silent > ~/volcasamples/patch.txt

Check how those files sound
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The `audition` command in its normal form will play to us each sample
in turn. We can repeat this command to decide which samples to include
and which to leave out::

    $ ~/py3-vs/bin/volcasample audition

    Auditioning project at ~/volcasamples

    0000000000111111111122.....6666666666777777777788888888889999999999
    0123456789012345678901.....0123456789012345678901234567890123456789
    .::.:::.:..:     :    .....       :Iiiii:iIIiiiiiiiIiiiIiiiiiiiiiii

The output is the same as before but as each symbol appears, the sample
it relates to is played. This takes longer than the ``--silent``
version of the command.

Define which files to send
~~~~~~~~~~~~~~~~~~~~~~~~~~

Use a text editor to open the file we created earlier, eg::

    $ vim ~/volcasamples/patch.txt

In order to make sure that our favourite samples get sent to the Volca,
we leave unchanged the symbols which sit in those slots. But
we have two options for the slots whose samples we don't have use for:

* Leave that slot unchanged on the Volca because we don't think it's
  taking much space
* Delete the sample in that slot to free up space for the ones we like

In your text editor, change the symbol to a space if you want to
preserve the sound which the Volca stores in that slot. Change the
symbol to an `X` to delete it:

.. code-block:: none

    0000000000111111111122.....6666666666777777777788888888889999999999
    0123456789012345678901.....0123456789012345678901234567890123456789
    .::.:::.:..:XXXXX:XXXX.....XXXXXXX:Iiiii:iIXiiiiiiiIXXXXXXXXXXXXXXX

Save the patch file again when you have finished.

Create a patch for the Volca device
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Direct your edited patch file into the `patch` command::

    $ ~/py3-vs/bin/volcasample patch --silent < ~/volcasamples/patch.txt

The program will create a `volcasamples.wav` file which you must play
into your Volca's `sync` input. Alternatively, you can omit the
``--silent`` flag and the patch pattern will play immediately.
