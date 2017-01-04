#!/usr/bin/env python3
# encoding: UTF-8

import unittest

import pkg_resources

class DiscoveryTests(unittest.TestCase):

    def test_find_so(self):
        print(pkg_resources.resource_listdir("volcasample", "lib"))
        self.fail()
