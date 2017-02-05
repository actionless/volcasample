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
from volcasample.syro import DataType
from volcasample.syro import Endian
from volcasample.syro import Handle
from volcasample.syro import Status
from volcasample.syro import SyroData


def sinedata(fW, durn=1, fSa=44100):
    gain = 2 ** 15
    samples = [gain * math.sin(i * 2 * math.pi * fW / fSa) for i in range(durn * fSa)]
    return b"".join(
        int(i).to_bytes(2, byteorder=sys.byteorder, signed=True)
        for i in samples)


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
        wav.writeframes(data)


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
            volcasample.syro.DataType.Sample_Compress.value.value,
            buf, 0, len(buf), nBits, freqS,
            volcasample.syro.Endian.LittleEndian.value.value,
        )
        self.assertEqual(91208, get_frame_size_sample_comp(data))

class SamplePackerTests(unittest.TestCase):

    @unittest.skip("Verification of test data")
    def test_sinedata(self):
        sinewave(sinedata(800))

    def test_start_raises_warning_with_status(self):
        patch = (SyroData * 1)()
        patch[0].DataType = DataType.Sample_Compress.value
        patch[0].Number = 500
        handle = Handle()
        self.assertRaises(
            RuntimeWarning,
            volcasample.syro.SamplePacker.start,
            handle,
            patch[0],
            1
        )
        try:
            volcasample.syro.SamplePacker.start(handle, patch[0], 1)
        except RuntimeWarning as e:
            self.assertIsInstance(e.args[0], Status)

    def test_start_returns_integer(self):
        patch = (SyroData * 1)()
        patch[0].DataType = DataType.Sample_Compress.value
        patch[0].Number = 1
        handle = Handle()
        nFrames = volcasample.syro.SamplePacker.start(handle, patch[0], 1)
        self.assertEqual(104392, nFrames)

    @unittest.skip("Until....")
    def test_end(self):
        handle = volcasample.syro.Handle()
        status = volcasample.syro.SamplePacker.start(handle, None)
        status = volcasample.syro.SamplePacker.end(handle)
        self.fail(status)

    def test_build_sine(self):
        def pointer_to_data(data):
            return ctypes.cast(
                ctypes.addressof(data),
                ctypes.POINTER(ctypes.c_uint8)
            )

        patch = (SyroData * 10)()
        data = sinedata(800)
        self.assertEqual(88200, len(data))
        patch[0].Number = 0
        patch[0].pData = pointer_to_data(ctypes.create_string_buffer(data))
        patch[0].Size = len(data)
        patch[0].Quality = 16
        patch[0].Fs = 44100
        patch[0].SampleEndian = (
            Endian.LittleEndian.value if sys.byteorder == "little"
            else Endian.BigEndian.value)
        patch[0].DataType = DataType.Sample_Compress.value
        handle = Handle()
        nFrames = volcasample.syro.SamplePacker.start(handle, patch[0], 1)
        print("OK so far.")
        self.assertEqual(1342352, nFrames)
        #for i in range(nFrames):
        #    print(i)
        #    rv = volcasample.syro.SamplePacker.get_sample(handle)
        #    self.assertIsInstance(rv, tuple, msg=i)
        #    self.assertEqual(2, len(rv))
        status = volcasample.syro.SamplePacker.end(handle)
        print(status)

    @unittest.skip("Until....")
    def test_build(self):
        patch = (SyroData * 100)()
        sample = pkg_resources.resource_filename(
            "volcasample.test", "data/pcm1608m.wav"
        )
        with open(sample, "r+b") as in_:
            data = in_.read()
        patch[0].pData.value = data
 
