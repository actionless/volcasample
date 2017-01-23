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

def get_comp_size(lib=None):
    lib = lib or pick_lib()
    fn = lib.SyroComp_GetCompSize
    fn.argtypes = [ctypes.POINTER(ctypes.c_ushort)]
    fn.errcheck = check
    rv = fn()
    return rv

