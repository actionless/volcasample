#!/usr/bin/env python3
# encoding: UTF-8

import ctypes
import enum
import os.path
import pkg_resources

# TODO: See korg_syro_volcasample_example setup_file_sample

def lib_paths(pkg="volcasample", locn="lib"):
    dirPath = pkg_resources.resource_filename(pkg, locn)
    return (
        os.path.join(dirPath, fN)
        for fN in pkg_resources.resource_listdir(pkg, locn)
    )

def pick_lib(pkg="volcasample", locn="lib"):
    return ctypes.cdll.LoadLibrary(next(lib_paths(pkg, locn)))

@enum.unique
class Endian(enum.Enum):
    LittleEndian = ctypes.c_uint(0)
    BigEndian = ctypes.c_uint(1)

@enum.unique
class DataType(enum.Enum):
    Sample_Liner = ctypes.c_uint(0)
    Sample_Compress = ctypes.c_uint(1)
    Sample_Erase = ctypes.c_uint(2)
    Sample_All = ctypes.c_uint(3)
    Sample_AllCompress = ctypes.c_uint(4)
    Pattern = ctypes.c_uint(5)

@enum.unique
class Status(enum.Enum):
    Success = ctypes.c_uint(0)
    IllegalDataType = ctypes.c_uint(1)
    IllegalData = ctypes.c_uint(2)
    IllegalParameter = ctypes.c_uint(3)
    OutOfRange_Number = ctypes.c_uint(4)
    OutOfRange_Quality = ctypes.c_uint(5)
    NotEnoughMemory = ctypes.c_uint(6)
    InvalidHandle = ctypes.c_uint(7)
    NoData = ctypes.c_uint(8)

Handle = ctypes.c_void_p



class SyroData(ctypes.Structure):

    _fields_  = [
        ("DataType", ctypes.c_uint),
        ("pData", ctypes.POINTER(ctypes.c_ubyte)),
        ("Number", ctypes.c_uint32),
        ("Size", ctypes.c_uint32),
        ("Quality", ctypes.c_uint32),
        ("Fs", ctypes.c_uint32),
        ("SampleEndian", ctypes.c_uint),
    ]

class SamplePacker:

    @staticmethod
    def build(assets):
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
            # TODO: return left, right
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

