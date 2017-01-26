#!/usr/bin/env python3
# encoding: UTF-8

import operator
import sys
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
        with wave.open(stereo, "rb") as data:
            rv = Audio.wav_to_mono(data, "test.wav")
            self.assertEqual(1, rv.getnchannels())
