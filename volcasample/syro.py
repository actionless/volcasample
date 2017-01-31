#!/usr/bin/env python3
# encoding: UTF-8

import ctypes
import enum
import os.path
import pkg_resources

"""
korg_syro_volcasample_example:

    See analyze_commandline for modes of operation.

	SyroData syro_data[MAX_SYRO_DATA];
	SyroStatus status;
	SyroHandle handle;
"""
"""

korg_syro_volcasample:

SyroStatus SyroVolcaSample_Start(SyroHandle *pHandle, SyroData *pData, int NumOfData,
	uint32_t Flags, uint32_t *pNumOfSyroFrame)

"""
"""
uint32_t SyroComp_GetCompSize(const uint8_t *psrc, uint32_t num_of_sample,
	uint32_t quality, Endian sample_endian);

uint32_t SyroComp_Comp(const uint8_t *psrc, uint8_t *pdest, int num_of_sample, 
	int quality, Endian sample_endian);
"""

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
        ("Number", ctypes.c_uint),
        ("Size", ctypes.c_uint),
        ("Quality", ctypes.c_uint),
        ("Fs", ctypes.c_uint),
        ("SampleEndian", ctypes.c_uint),
    ]

class SamplePacker:

    @staticmethod
    def start(handle, nSamples=100, lib=None):

        def check(result, fn, args):
            return next(
                (i for i in Status if i.value.value == result),
                None
            )

        lib = lib or pick_lib()
        handle = Handle()
        buf = (SyroData * nSamples)()
        flags = 0
        nFrame = ctypes.c_uint()
        fn = lib.SyroVolcaSample_Start
        fn.argtypes = [
            ctypes.POINTER(Handle),
            ctypes.POINTER(SyroData),
            ctypes.c_int,
            ctypes.c_uint,
            ctypes.POINTER(ctypes.c_uint)
        ]
        fn.errcheck = check
        return fn(
            ctypes.byref(handle),
            buf,
            nSamples,
            0,
            ctypes.byref(nFrame)
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
        fn.argtypes = [ctypes.POINTER(Handle)]
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

