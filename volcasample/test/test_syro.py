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

class SyroCompTests(unittest.TestCase):

    def test_GetCompSize(self):
        self.fail()
        get_comp_size()
