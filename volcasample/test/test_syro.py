#!/usr/bin/env python3
# encoding: UTF-8

import ctypes
import unittest

import volcasample.syro
from volcasample.syro import get_comp_size
from volcasample.syro import pick_lib


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

class SyroCompTests(unittest.TestCase):

    def test_GetCompSize(self):
        self.fail()
        get_comp_size()
