#!/usr/bin/env python3
# encoding: UTF-8

# This file is part of volcasample.
#
# volcasample is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# volcasample is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with volcasample.  If not, see <http://www.gnu.org/licenses/>.

import ctypes
import enum
import os.path
import pkg_resources
import struct
import sys
import wave


def lib_paths(pkg="volcasample", locn="lib/volcasample"):
    dirPath = pkg_resources.resource_filename(pkg, locn)
    return (
        os.path.join(dirPath, fN)
        for fN in pkg_resources.resource_listdir(pkg, locn)
    )


def pick_lib(pkg="volcasample", locn="lib/volcasample"):
    return ctypes.cdll.LoadLibrary(next(lib_paths(pkg, locn)))


@enum.unique
class Endian(enum.Enum):
    """
    Shadows the Endian enumeration in the Syro C library.

    """
    LittleEndian = ctypes.c_uint32(0)
    BigEndian = ctypes.c_uint32(1)


@enum.unique
class DataType(enum.Enum):
    """
    Shadows the DataType enumeration in the Syro C library.

    """
    Sample_Liner = ctypes.c_uint32(0)
    Sample_Compress = ctypes.c_uint32(1)
    Sample_Erase = ctypes.c_uint32(2)
    Sample_All = ctypes.c_uint32(3)
    Sample_AllCompress = ctypes.c_uint32(4)
    Pattern = ctypes.c_uint32(5)


@enum.unique
class Status(enum.Enum):
    """
    Shadows the Status enumeration in the Syro C library.

    """
    Success = ctypes.c_uint32(0)
    IllegalDataType = ctypes.c_uint32(1)
    IllegalData = ctypes.c_uint32(2)
    IllegalParameter = ctypes.c_uint32(3)
    OutOfRange_Number = ctypes.c_uint32(4)
    OutOfRange_Quality = ctypes.c_uint32(5)
    NotEnoughMemory = ctypes.c_uint32(6)
    InvalidHandle = ctypes.c_uint32(7)
    NoData = ctypes.c_uint32(8)


Handle = ctypes.c_void_p  #: An opaque pointer to an internal library structure.


class SyroData(ctypes.Structure):
    """
    Shadows the SyroData structure in the Syro C library.

    """
    _fields_  = [
        ("DataType", ctypes.c_uint32),
        ("pData", ctypes.c_char_p),
        ("Number", ctypes.c_uint32),
        ("Size", ctypes.c_uint32),
        ("Quality", ctypes.c_uint32),
        ("Fs", ctypes.c_uint32),
        ("SampleEndian", ctypes.c_uint32),
    ]


class SamplePacker:
    """
    This class contains all the methods needed to program a
    Volca Sample device.

    #. Use :py:meth:`volcasample.syro.SamplePacker.patch` to populate
       patch data.
    #. Produce a data file from the patch with
       :py:meth:`volcasample.syro.SamplePacker.build`.

    """

    @staticmethod
    def patch(jobs):
        """
        :param jobs: An OrderedDict of
         {int: (:py:class:`volcasample.syro.DataType`, str)}.

             * The keys are indexes of sample slots (0 - 99).
             * Values are 2-tuples, such that:

                #. First element determines whether to load
                   or delete the slot.
                #. Second element is a path to an audio sample
                   file.

        :return: An array containing patch data.
        :rtype: [SyroData]
        """
        rv = (SyroData * len(jobs))()
        for i, (n, (dt, fP)) in enumerate(jobs.items()):
            rv[i].Number = n
            if dt == DataType.Sample_Compress:
                with wave.open(fP, "rb") as wav:
                    data = wav.readframes(wav.getnframes())
                rv[i].pData = ctypes.c_char_p(data)
                rv[i].Size = len(data)
                rv[i].Quality = 8 * wav.getsampwidth()
                assert 8 <= rv[i].Quality <= 16, fP
                rv[i].Fs = wav.getframerate()
            else:
                rv[i].pData = None
                rv[i].Size = 0

            rv[i].SampleEndian = (
                Endian.LittleEndian.value if sys.byteorder == "little"
                else Endian.BigEndian.value)
            rv[i].DataType = dt.value

        return rv

    @staticmethod
    def build(patch, locn=None, output="volcasamples.wav"):
        """
        Create a WAV file with patch data for a Volca device.

        :param [SyroData] patch: An array containing patch data.
        :param str locn: A path to a writeable directory.
        :param str output: The name of the output file.
        :return: A 2-tuple of (status, file path).
        :rtype: tuple

        """
        locn = locn or os.path.expanduser("~")
        fP = os.path.join(locn, output)
        handle = Handle()
        try:
            nFrames = SamplePacker.start(handle, patch, len(patch))
            rv = list(SamplePacker.get_samples(handle, nFrames))

            with wave.open(fP, "wb") as wav:
                wav.setparams(wave._wave_params(
                    nchannels=2,
                    sampwidth=2,
                    framerate=44100,
                    nframes=nFrames,
                    comptype="NONE",
                    compname="not compressed"
                ))
                for l, r in rv:
                    wav.writeframesraw(struct.pack("<hh", l, r))

        finally:
            return (SamplePacker.end(handle), fP)

    @staticmethod
    def start(handle, data, nEntries, lib=None):
        """
        This method wraps the SyroVolcaSample_Start function.

        :param Handle handle: A fresh handle object.
        :param [SyroData] data: An array containing patch data.
        :param int nEntries: The number of elements in the array.
        :return: Number of output frames.
        :rtype: int

        """
        assert 0 <= nEntries <= 110

        def check(result, fn, args):
            status = next(
                (i for i in Status if i.value.value == result),
                None
            )
            if status is not Status.Success:
                raise RuntimeWarning(status)
            return args[-1].contents.value

        lib = lib or pick_lib()
        flags = 0
        nFrame = ctypes.c_uint32()
        fn = lib.SyroVolcaSample_Start
        fn.argtypes = [
            ctypes.POINTER(Handle),
            ctypes.POINTER(SyroData),
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.POINTER(ctypes.c_uint32)
        ]
        fn.errcheck = check
        return fn(
            handle,
            data,
            nEntries,
            0,
            ctypes.pointer(nFrame)
        )

    @staticmethod
    def wrap_sample_fn(lib=None):
        lib = lib or pick_lib()
        fn = lib.SyroVolcaSample_GetSample
        fn.argtypes = [
            Handle,
            ctypes.POINTER(ctypes.c_int16),
            ctypes.POINTER(ctypes.c_int16),
        ]
        return fn

    @staticmethod
    def get_sample(handle, lib=None):

        def check(result, fn, args):
            status = next(
                (i for i in Status if i.value.value == result),
                None
            )
            if status is not Status.Success:
                raise RuntimeWarning(status)
            return tuple(i.contents.value for i in args[-2:])

        fn = SamplePacker.wrap_sample_fn()
        fn.errcheck = check
        left = ctypes.c_int16()
        right = ctypes.c_int16()
        return fn(handle, ctypes.pointer(left), ctypes.pointer(right))

    @staticmethod
    def get_samples(handle, nFrames, lib=None):
        """
        This method wraps the SyroVolcaSample_GetSample function.

        :param Handle handle: A fresh handle object.
        :param int nFrames: The number of sample frames to be returned.
        :return: A sequence of stereo (2-tuple) samples.
        :rtype: generator

        """
        fn = SamplePacker.wrap_sample_fn()
        fn.restype = ctypes.c_uint8
        left = ctypes.c_int16()
        leftPtr = ctypes.pointer(left)
        right = ctypes.c_int16()
        rightPtr = ctypes.pointer(right)

        return (
            (leftPtr.contents.value, rightPtr.contents.value)
            for i in range(nFrames)
            if not fn(handle, leftPtr, rightPtr)
        )

    @staticmethod
    def end(handle, lib=None):
        """
        This method wraps the SyroVolcaSample_End function.

        :param Handle handle: A fresh handle object.
        :return: Syro C library status.
        :rtype: Status

        """

        def check(result, fn, args):
            return next(
                (i for i in Status if i.value.value == result),
                None
            )

        lib = lib or pick_lib()
        fn = lib.SyroVolcaSample_End
        fn.argtypes = [Handle]
        fn.errcheck = check
        return fn(handle)

    @staticmethod
    def get_frame_size_sample_comp(data, lib=None):

        def check(result, fn, args):
            return result

        lib = lib or pick_lib()
        fn = lib.SyroVolcaSample_GetFrameSize_Sample_Comp
        fn.argtypes = [ctypes.POINTER(SyroData)]
        fn.restype = ctypes.c_uint
        fn.errcheck = check
        rv = fn(data)
        return rv
