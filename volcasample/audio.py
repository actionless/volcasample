#!/usr/bin/env python3
# encoding: UTF-8

import operator
import sys
import unittest
import wave

import pkg_resources

try:
    import simplesound
except ImportError:
    simplesound = None

class Audio:

    @staticmethod
    def metadata(params, path=None):
        rv = OrderedDict(
            [(k, getattr(metadata, k)) for k in params._fields]
        )
        if path is not None:
            rv["path"] = path
            rv.move_to_end("path", last=False)
        return rv

    @staticmethod
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

    @staticmethod
    def find_peaks(stereo):
        leftMin, leftMax = [
            fn(map(operator.itemgetter(0), stereo))
            for fn in (min, max)
        ]
        rightMin, rightMax = [
            fn(map(operator.itemgetter(1), stereo))
            for fn in (min, max)
        ]
        return leftMin, leftMax, rightMin, rightMax

    @staticmethod
    def stereo_to_mono(stereo):
        return [
            (left + right) // 2
            for left, right in stereo
        ]

    @staticmethod
    def wav_to_mono(wav, output):
        nChannels = wav.getnchannels()
        if nChannels == 1:
            return wav

        bytesPerSample = wav.getsampwidth()
        nFrames = wav.getnframes()
        raw = wav.readframes(nFrames)
        data = Audio.extract_samples(
            raw, nChannels, bytesPerSample, nFrames
        )
        mono = Audio.stereo_to_mono(data)

        with wave.open(output, mode="wb") as rv:
            rv.setparams(wav.getparams())
            rv.setnchannels(1)
            try:
                rv.writeframes(
                    b"".join(
                        int(i).to_bytes(
                            bytesPerSample,
                            byteorder="little",
                            signed=True
                        )
                        for i in mono
                    )
                )
            except OverflowError as e:
                print(min(mono))
                print(max(mono))
                raise
            return rv
