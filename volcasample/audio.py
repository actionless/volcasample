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
            [(k, getattr(params, k)) for k in params._fields]
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
        if bytesPerSample == 3:
            lift = max(max(mono), abs(min(mono))) / 2**16
            mono = [i // lift for i in mono]

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
