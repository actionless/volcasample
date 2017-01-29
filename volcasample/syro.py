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

def check(result, fn, args):
    print(result, fn, args)

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

"""
typedef struct {
    SyroDataType DataType;
    uint8_t *pData;
    uint32_t Number;		// Sample:0-99, Pattern:0-9
    uint32_t Size;			// Byte Size (if type=Sample)
    uint32_t Quality;		// specific Sample bit (8-16), if type=LossLess
	uint32_t Fs;
	Endian SampleEndian;
} SyroData;
"""

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

def get_frame_size_sample_comp(data, lib=None):
    lib = lib or pick_lib()
    fn = lib.SyroComp_GetFrameSize_Sample_Comp
    fn.argtypes = [POINTER(SyroData)]
    fn.errcheck = check
    rv = fn(data)
    return rv

