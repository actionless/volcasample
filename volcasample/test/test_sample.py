#!/usr/bin/env python3
# encoding: UTF-8

import math
import operator
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

def find_peaks(stereo):
    leftMin, leftMax = [fn(map(operator.itemgetter(0), stereo)) for fn in (min, max)]
    rightMin, rightMax = [fn(map(operator.itemgetter(1), stereo)) for fn in (min, max)]
    return leftMin, leftMax, rightMin, rightMax

def mix_to_mono(stereo):
    peaks = find_peaks(stereo)
    posMax, negMin = max(peaks), min(peaks)
    threshold = posMax / 2 ** 6

    signs = [
        -1 if abs(
            posMax and max(left, right) / posMax
        ) < abs(
            negMin and min(left, right) / negMin
        ) else 1
        for left, right in stereo
    ]

    signs = [
        -1 if abs(
            negMin and min(left, right) / negMin
        ) - abs(
            posMax and max(left, right) / posMax
        ) > threshold else 1
        for left, right in stereo
    ]

    sqrt = math.sqrt
    sqrtOf2 = sqrt(2)
    vals = [
        sqrt(left * left + right * right) / sqrtOf2
        for left, right in stereo
    ]
    return [sign * val for sign, val in zip(signs, vals)]

def to_mono(wav, output):
    nChannels = wav.getnchannels()
    if nChannels == 1:
        return wav

    bytesPerSample = wav.getsampwidth()
    nFrames = wav.getnframes()
    raw = wav.readframes(nFrames)
    data = extract_samples(
        raw, nChannels, bytesPerSample, nFrames
    )
    mix = mix_to_mono(data)

    with wave.open(output, mode="wb") as rv:
        rv.setparams(wav.getparams())
        rv.setnchannels(1)
        rv.writeframes(
            b"".join(
                int(i).to_bytes(
                    bytesPerSample,
                    byteorder="little",
                    signed=True
                )
                for i in mix
            )
        )
        return rv

class ConversionTests(unittest.TestCase):

    @staticmethod
    def extract_wav_data(fP):
        with wave.open(fP, "rb") as wav:
            nChannels = wav.getnchannels()
            bytesPerSample = wav.getsampwidth()
            nFrames = wav.getnframes()
            raw = wav.readframes(nFrames)
            data = extract_samples(
                raw, nChannels, bytesPerSample, nFrames
            )
            return wav, data

    def test_read_samples(self):
        stereoFP  = pkg_resources.resource_filename(
            "volcasample.test", "data/380_gunshot_single-mike-koenig-short.wav"
        )

        wav, data = ConversionTests.extract_wav_data(stereoFP)
        nFrames = wav.getnframes()
        self.assertEqual(nFrames, len(data))
        self.assertEqual((32767, 30163), max(data))
        self.assertEqual((-32768, -32765), min(data))

    def test_find_peaks(self):
        stereoFP  = pkg_resources.resource_filename(
            "volcasample.test", "data/380_gunshot_single-mike-koenig-short.wav"
        )

        wav, data = ConversionTests.extract_wav_data(stereoFP)
        self.assertEqual(32767, max(find_peaks(data)))
        self.assertEqual(-32768, min(find_peaks(data)))

    def test_mix_to_mono(self):
        self.assertEqual([0], mix_to_mono([(0, 0)]))
        self.assertEqual([1], mix_to_mono([(1, 1)]))
        self.assertEqual([1], mix_to_mono([(1, -1)]))
        self.assertEqual([1, -1 / math.sqrt(2)], mix_to_mono([(1, -1), (0, -1)]))

    def test_stereo_to_mono(self):
        stereo  = pkg_resources.resource_filename(
            "volcasample.test", "data/380_gunshot_single-mike-koenig-short.wav"
        )
        with wave.open(stereo, "rb") as data:
            rv = to_mono(data, "test.wav")

        self.fail()
