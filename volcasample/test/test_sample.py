#!/usr/bin/env python3
# encoding: UTF-8

import sys
import unittest
import wave

import pkg_resources

def extract_samples(
        raw,
        nChannels,
        bytesPerSample,
        nFrames,
        endian=sys.byteorder,
        signed=True
    ):
    nBytes = nChannels * bytesPerSample * nFrames
    i0, i1, = (bytesPerSample * i for i in (1, nChannels))
    return [(
        int.from_bytes(raw[pos:pos + i0], endian, signed=True),
        int.from_bytes(raw[pos + i0: pos + i1], endian, signed=True))
        for pos in range(0, nBytes, bytesPerSample * nChannels)]

def to_mono(wav):
    nChannels = wav.getnchannels()
    if nChannels == 1:
        return wav

    bytesPerSample = wav.getsampwidth()
    nFrames = wav.getnframes()
    raw = wav.readframes(nFrames)
    data = extract_samples(
        raw, nChannels, bytesPerSample, nFrames
    )
 
    return data

class ConversionTests(unittest.TestCase):

    def test_read_samples(self):
        stereo  = pkg_resources.resource_filename(
            "volcasample.test", "data/380_gunshot_single-mike-koenig-short.wav"
        )
        with wave.open(stereo, "rb") as wav:
            nChannels = wav.getnchannels()
            bytesPerSample = wav.getsampwidth()
            nFrames = wav.getnframes()
            raw = wav.readframes(nFrames)
            rv = extract_samples(
                raw, nChannels, bytesPerSample, nFrames
            )

        self.assertEqual(nFrames, len(rv))
        self.assertEqual((32767, 30163), max(rv))
        self.assertEqual((-32768, -32765), min(rv))

    def test_stereo_to_mono(self):
        stereo  = pkg_resources.resource_filename(
            "volcasample.test", "data/380_gunshot_single-mike-koenig-short.wav"
        )
        with wave.open(stereo, "rb") as data:
            rv = to_mono(data)

        self.fail()
