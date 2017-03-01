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

from collections import OrderedDict
import ctypes
import math
import os.path
import struct
import sys
import tempfile
import unittest
import wave

import pkg_resources

import volcasample.syro
from volcasample.syro import pick_lib
from volcasample.syro import DataType
from volcasample.syro import Endian
from volcasample.syro import Handle
from volcasample.syro import Status
from volcasample.syro import SyroData


def sinedata(fW, durn=1, fSa=44100):
    offset = 1
    gain = 2 ** 14
    samples = [
        gain * (
            offset + math.sin(i * 2 * math.pi * fW / fSa)
        )
        for i in range(durn * fSa)]
    return b"".join(
        int(i).to_bytes(2, byteorder=sys.byteorder, signed=False)
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
        self.assertEqual(
            91208,
            volcasample.syro.SamplePacker.get_frame_size_sample_comp(data)
        )

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
        patch[0].Quality = 16
        patch[0].pData = ctypes.c_char_p(b"")
        patch[0].Size = 0
        handle = Handle()
        try:
            nFrames = volcasample.syro.SamplePacker.start(handle, patch[0], 1)
            self.assertEqual(107488, nFrames)
        finally:
            status = volcasample.syro.SamplePacker.end(handle)
            self.assertIs(status, Status.Success)

    def test_build_sine(self):
        patch = (SyroData * 10)()
        data = sinedata(800)
        self.assertEqual(88200, len(data))
        patch[0].Number = 0
        patch[0].pData = ctypes.c_char_p(data)
        patch[0].Size = len(data)
        patch[0].Quality = 16
        patch[0].Fs = 44100
        patch[0].SampleEndian = (
            Endian.LittleEndian.value if sys.byteorder == "little"
            else Endian.BigEndian.value)
        patch[0].DataType = DataType.Sample_Compress.value
        handle = Handle()
        try:
            nFrames = volcasample.syro.SamplePacker.start(handle, patch[0], 1)
            self.assertEqual(881048, nFrames)
            rv = list(volcasample.syro.SamplePacker.get_samples(handle, nFrames))
            self.assertEqual(nFrames, len(rv))
            self.assertTrue(all(isinstance(i, tuple) for i in rv))
            self.assertTrue(all(len(i) == 2 for i in rv))
        finally:
            status = volcasample.syro.SamplePacker.end(handle)
            self.assertIs(status, Status.Success)

    @unittest.skip("Slow test")
    def test_build_sine_slow(self):
        patch = (SyroData * 10)()
        data = sinedata(800)
        self.assertEqual(88200, len(data))
        patch[0].Number = 0
        patch[0].pData = ctypes.c_char_p(data)
        patch[0].Size = len(data)
        patch[0].Quality = 16
        patch[0].Fs = 44100
        patch[0].SampleEndian = (
            Endian.LittleEndian.value if sys.byteorder == "little"
            else Endian.BigEndian.value)
        patch[0].DataType = DataType.Sample_Compress.value
        handle = Handle()
        try:
            nFrames = volcasample.syro.SamplePacker.start(handle, patch[0], 1)
            self.assertEqual(946064, nFrames)
            for i in range(nFrames):
                rv = volcasample.syro.SamplePacker.get_sample(handle)
                self.assertIsInstance(rv, tuple, msg=i)
                self.assertEqual(2, len(rv))
        finally:
            status = volcasample.syro.SamplePacker.end(handle)
            self.assertIs(status, Status.Success)

    def test_patch_24bit(self):
        sample = pkg_resources.resource_filename(
            "volcasample.test", "data/chinese-gong-daniel_simon.wav"
        )
        jobs = OrderedDict([
            (0, (DataType.Sample_Compress, sample))
        ])
        self.assertRaises(
            AssertionError,
            volcasample.syro.SamplePacker.patch,
            jobs
        )

    def test_patch(self):
        sample = pkg_resources.resource_filename(
            "volcasample.test", "data/pcm1608m.wav"
        )
        jobs = OrderedDict([
            (0, (DataType.Sample_Compress, sample))
        ])
        rv = volcasample.syro.SamplePacker.patch(jobs)
        self.assertIsInstance(rv, SyroData * 1)
        self.assertEqual(1, rv[0].DataType)

    def test_manual_patch_sine(self):
        patch = (SyroData * 1)()
        data = sinedata(440)
        patch[0].Number = 0
        patch[0].pData = ctypes.c_char_p(data)
        patch[0].Size = len(data)
        patch[0].Quality = 16
        patch[0].Fs = 44100
        patch[0].SampleEndian = (
            Endian.LittleEndian.value if sys.byteorder == "little"
            else Endian.BigEndian.value)
        patch[0].DataType = DataType.Sample_Compress.value

        fD, fP = tempfile.mkstemp(suffix=".wav")
        try:
            status, rv = volcasample.syro.SamplePacker.build(
                patch, *os.path.split(fP)
            )
            self.assertIs(status, Status.Success)
            self.assertEqual(fP, rv)
            with wave.open(fP, "rb") as wav:
                params = wav.getparams()._asdict()
                nFrames = params.pop("nframes")
                self.assertEqual(
                    dict(
                        nchannels=2, sampwidth=2, framerate=44100,
                        comptype="NONE",
                        compname="not compressed"
                    ),
                    params
                , params)
                self.assertEqual(778880, nFrames) 
        finally:
            os.close(fD)
            os.remove(fP)

    def test_build_wav(self):
        patch = (SyroData * 1)()
        sample = pkg_resources.resource_filename(
            "volcasample.test", "data/pcm1608m.wav"
        )
        with wave.open(sample, "rb") as wav:
            data = wav.readframes(wav.getnframes())
        patch[0].Number = 0
        patch[0].pData = ctypes.c_char_p(data)
        patch[0].Size = len(data)
        patch[0].Quality = 8 * wav.getsampwidth()
        patch[0].Fs = wav.getframerate()
        patch[0].SampleEndian = (
            Endian.LittleEndian.value if sys.byteorder == "little"
            else Endian.BigEndian.value)
        patch[0].DataType = DataType.Sample_Compress.value

        fD, fP = tempfile.mkstemp(suffix=".wav")
        try:
            status, rv = volcasample.syro.SamplePacker.build(
                patch, *os.path.split(fP)
            )
            self.assertIs(status, Status.Success)
            self.assertEqual(fP, rv)
            with wave.open(fP, "rb") as wav:
                params = wav.getparams()._asdict()
                nFrames = params.pop("nframes")
                self.assertEqual(
                    dict(
                        nchannels=2, sampwidth=2, framerate=44100,
                        comptype="NONE",
                        compname="not compressed"
                    ),
                    params
                , params)
                self.assertEqual(1501696, nFrames) 
        finally:
            os.close(fD)
            os.remove(fP)
