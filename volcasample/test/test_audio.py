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

import operator
import os
import sys
import tempfile
import unittest
import wave

import pkg_resources

from volcasample.audio import Audio

class ConversionTests(unittest.TestCase):

    @staticmethod
    def extract_wav_data(fP):
        with wave.open(fP, "rb") as wav:
            nChannels = wav.getnchannels()
            bytesPerSample = wav.getsampwidth()
            nFrames = wav.getnframes()
            raw = wav.readframes(nFrames)
            data = Audio.extract_samples(
                raw, nChannels, bytesPerSample, nFrames
            )
            return wav, data

    def test_read_samples(self):
        stereoFP  = pkg_resources.resource_filename(
            "volcasample.test",
            "data/380_gunshot_single-mike-koenig-short.wav"
        )

        wav, data = ConversionTests.extract_wav_data(stereoFP)
        nFrames = wav.getnframes()
        self.assertEqual(nFrames, len(data))
        self.assertEqual((32767, 30163), max(data))
        self.assertEqual((-32768, -32765), min(data))

    def test_find_peaks(self):
        stereoFP  = pkg_resources.resource_filename(
            "volcasample.test",
            "data/380_gunshot_single-mike-koenig-short.wav"
        )

        wav, data = ConversionTests.extract_wav_data(stereoFP)
        self.assertEqual(32767, max(Audio.find_peaks(data)))
        self.assertEqual(-32768, min(Audio.find_peaks(data)))

    def test_stereo_to_mono(self):
        self.assertEqual([0], Audio.stereo_to_mono([(0, 0)]))
        self.assertEqual([1], Audio.stereo_to_mono([(1, 1)]))
        self.assertEqual([0], Audio.stereo_to_mono([(1, -1)]))
        self.assertEqual(
            [0, -1],
            Audio.stereo_to_mono([(1, -1), (0, -1)])
        )

    def test_wav_to_mono(self):
        stereo  = pkg_resources.resource_filename(
            "volcasample.test",
            "data/380_gunshot_single-mike-koenig-short.wav"
        )
        fD, fP = tempfile.mkstemp(suffix=".wav")
        try:
            with wave.open(stereo, "rb") as data:
                rv = Audio.wav_to_mono(data, fP)
                self.assertEqual(1, rv.getnchannels())
        finally:
            os.close(fD)
            os.remove(fP)

    def test_wav_to_mono_24bit(self):
        stereoFP  = pkg_resources.resource_filename(
            "volcasample.test",
            "data/chinese-gong-daniel_simon.wav"
        )

        wav, data = ConversionTests.extract_wav_data(stereoFP)
        self.assertEqual(8388607, max(Audio.find_peaks(data)))
        self.assertEqual(-8388608, min(Audio.find_peaks(data)))

        fD, fP = tempfile.mkstemp(suffix=".wav")
        try:
            with wave.open(stereoFP, "rb") as data:
                rv = Audio.wav_to_mono(data, fP)
                self.assertEqual(1, rv.getnchannels())

            wav, data = ConversionTests.extract_wav_data(fP)
            self.assertEqual(32708, max(Audio.find_peaks(data)))
            self.assertEqual(-32768, min(Audio.find_peaks(data)))
        finally:
            os.close(fD)
            os.remove(fP)
