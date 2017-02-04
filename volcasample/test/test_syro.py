#!/usr/bin/env python3
# encoding: UTF-8

import ctypes
import math
import sys
import unittest
import wave

import pkg_resources

import volcasample.syro
from volcasample.syro import get_frame_size_sample_comp
from volcasample.syro import pick_lib
from volcasample.syro import SyroData


def sinedata(fW, durn=1, fSa=44100):
    gain = 2 ** 15
    return [gain * math.sin(i * 2 * math.pi * fW / fSa) for i in range(durn * fSa)]


def sinewave(data, fP="monosin441.wav", fSa=44100):
    with wave.open(fP, "wb") as wav:
        wav.setparams(wave._wave_params(
            nchannels=1,
            sampwidth=2,
            framerate=fSa,
            nframes=len(data),
            comptype="NONE",
            compname="not compressed"
        ))
        wav.writeframes(
            b"".join(
                int(i).to_bytes(2, byteorder=sys.byteorder, signed=True)
                for i in data
            )
        )


class DiscoveryTests(unittest.TestCase):

    def test_find_so(self):
        lib = pick_lib()
        self.assertIsInstance(lib, ctypes.CDLL)

class SyroTypeTests(unittest.TestCase):

    def test_endian(self):
        self.assertEqual(
            0,
            volcasample.syro.Endian.LittleEndian.value.value
        )
        self.assertEqual(
            1,
            volcasample.syro.Endian.BigEndian.value.value
        )

    def test_datatype(self):
        self.assertEqual(
            0,
            volcasample.syro.DataType.Sample_Liner.value.value
        )
        self.assertEqual(
            1,
            volcasample.syro.DataType.Sample_Compress.value.value
        )
        self.assertEqual(
            2,
            volcasample.syro.DataType.Sample_Erase.value.value
        )
        self.assertEqual(
            3,
            volcasample.syro.DataType.Sample_All.value.value
        )
        self.assertEqual(
            4,
            volcasample.syro.DataType.Sample_AllCompress.value.value
        )
        self.assertEqual(
            5,
            volcasample.syro.DataType.Pattern.value.value
        )

    def test_status(self):
        self.assertEqual(
            0,
            volcasample.syro.Status.Success.value.value
        )
        self.assertEqual(
            1,
            volcasample.syro.Status.IllegalDataType.value.value
        )
        self.assertEqual(
            2,
            volcasample.syro.Status.IllegalData.value.value
        )
        self.assertEqual(
            3,
            volcasample.syro.Status.IllegalParameter.value.value
        )
        self.assertEqual(
            4,
            volcasample.syro.Status.OutOfRange_Number.value.value
        )
        self.assertEqual(
            5,
            volcasample.syro.Status.OutOfRange_Quality.value.value
        )
        self.assertEqual(
            6,
            volcasample.syro.Status.NotEnoughMemory.value.value
        )
        self.assertEqual(
            7,
            volcasample.syro.Status.InvalidHandle.value.value
        )
        self.assertEqual(
            8,
            volcasample.syro.Status.NoData.value.value
        )

@unittest.skip("exposing static internal function for sanity check")
class SyroCompTests(unittest.TestCase):

    def test_GetFrameSizeSampleComp(self):
        buf = (ctypes.c_ubyte * 1024)()
        nBits = 16
        freqS = 44100
        qam = 16
        data = volcasample.syro.SyroData(
            volcasample.syro.DataType.Sample_Liner.value.value,
            buf, 0, len(buf), nBits, freqS,
            volcasample.syro.Endian.LittleEndian.value.value,
        )
        self.assertEqual(91208, get_frame_size_sample_comp(data))

class SamplePackerTests(unittest.TestCase):

    @unittest.skip("Until....")
    def test_start(self):
        handle = volcasample.syro.Handle()
        data = SyroData(0, handle, 1, 1, 16, 44100, 0)
        status = volcasample.syro.SamplePacker.start(
            handle, data[0]
        )
        self.fail(status)

    @unittest.skip("Until....")
    def test_end(self):
        handle = volcasample.syro.Handle()
        status = volcasample.syro.SamplePacker.start(handle, None)
        status = volcasample.syro.SamplePacker.end(handle)
        self.fail(status)

    def test_build_sine(self):
        sinewave(sinedata(800))

    @unittest.skip("Until....")
    def test_build(self):
        patch = (SyroData * 100)()
        sample = pkg_resources.resource_filename(
            "volcasample.test", "data/pcm1608m.wav"
        )
        with open(sample, "r+b") as in_:
            data = in_.read()
        patch[0].pData.value = data
        patch[0].Size = len(data)
 
