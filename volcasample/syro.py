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


def lib_paths(pkg="volcasample", locn="lib"):
    dirPath = pkg_resources.resource_filename(pkg, locn)
    return (
        os.path.join(dirPath, fN)
        for fN in pkg_resources.resource_listdir(pkg, locn)
    )


def pick_lib(pkg="volcasample", locn="lib"):
    return ctypes.cdll.LoadLibrary(next(lib_paths(pkg, locn)))


def point_to_bytememory(data):
	return ctypes.cast(
		ctypes.addressof(
			ctypes.create_string_buffer(data)
		),
		ctypes.POINTER(ctypes.c_uint8)
	)


@enum.unique
class Endian(enum.Enum):
    LittleEndian = ctypes.c_uint32(0)
    BigEndian = ctypes.c_uint32(1)


@enum.unique
class DataType(enum.Enum):
    Sample_Liner = ctypes.c_uint32(0)
    Sample_Compress = ctypes.c_uint32(1)
    Sample_Erase = ctypes.c_uint32(2)
    Sample_All = ctypes.c_uint32(3)
    Sample_AllCompress = ctypes.c_uint32(4)
    Pattern = ctypes.c_uint32(5)


@enum.unique
class Status(enum.Enum):
    Success = ctypes.c_uint32(0)
    IllegalDataType = ctypes.c_uint32(1)
    IllegalData = ctypes.c_uint32(2)
    IllegalParameter = ctypes.c_uint32(3)
    OutOfRange_Number = ctypes.c_uint32(4)
    OutOfRange_Quality = ctypes.c_uint32(5)
    NotEnoughMemory = ctypes.c_uint32(6)
    InvalidHandle = ctypes.c_uint32(7)
    NoData = ctypes.c_uint32(8)


Handle = ctypes.c_void_p


class SyroData(ctypes.Structure):

    _fields_  = [
        ("DataType", ctypes.c_uint32),
        ("pData", ctypes.POINTER(ctypes.c_uint8)),
        ("Number", ctypes.c_uint32),
        ("Size", ctypes.c_uint32),
        ("Quality", ctypes.c_uint32),
        ("Fs", ctypes.c_uint32),
        ("SampleEndian", ctypes.c_uint32),
    ]


class SamplePacker:

    @staticmethod
    def build(assets):
        # TODO: accept metadata, data, compress/skip/delete
        data = (SyroData * len(assets))()
        return data

    @staticmethod
    def start(handle, data, nEntries, lib=None):
        """
        Returns an integer number of output frames.

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
            ctypes.c_int,
            ctypes.c_uint,
            ctypes.POINTER(ctypes.c_uint32)
        ]
        fn.errcheck = check
        return fn(
            ctypes.byref(handle),
            ctypes.byref(data),
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
            ctypes.POINTER(ctypes.c_uint16),
            ctypes.POINTER(ctypes.c_uint16),
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
        left = ctypes.c_uint16()
        right = ctypes.c_uint16()
        return fn(handle, ctypes.pointer(left), ctypes.pointer(right))

    @staticmethod
    def get_samples(handle, nFrames, lib=None):
        fn = SamplePacker.wrap_sample_fn()
        fn.restype = ctypes.c_uint8
        left = ctypes.c_uint16()
        leftPtr = ctypes.pointer(left)
        right = ctypes.c_uint16()
        rightPtr = ctypes.pointer(right)

        return (
            (leftPtr.contents.value, rightPtr.contents.value)
            for i in range(nFrames) if not fn(handle, leftPtr, rightPtr)
        )

    @staticmethod
    def end(handle, lib=None):

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
