#!/usr/bin/env python3
# encoding: UTF-8

import unittest

import ctypes
import os.path
import pkg_resources

def lib_paths(pkg="volcasample", locn="lib"):
    dirPath = pkg_resources.resource_filename(pkg, locn)
    return (
        os.path.join(dirPath, fN)
        for fN in pkg_resources.resource_listdir(pkg, locn)
    )
    
class DiscoveryTests(unittest.TestCase):

    def test_find_so(self):
        lib = ctypes.cdll.LoadLibrary(next(lib_paths()))
        self.assertIsInstance(lib, ctypes.CDLL)
