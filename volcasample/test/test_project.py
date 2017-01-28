#!/usr/bin/env python3
# encoding: UTF-8

import os.path
import tempfile
import unittest

from volcasample.project import Project


class NeedsTempDirectory:

    def setUp(self):
        self.drcty = tempfile.TemporaryDirectory()

    def tearDown(self):
        if os.path.isdir(self.drcty.name):
            self.drcty.cleanup()
        self.assertFalse(os.path.isdir(self.drcty.name))
        self.drcty = None

class NewProjectTests(NeedsTempDirectory, unittest.TestCase):

    def test_all_subdirectories(self):
        Project.create(self.drcty.name, quiet=True)
        self.assertEqual(
            {"{0:02}".format(i) for i in range(100)},
            set(os.listdir(self.drcty.name))
        )

    def test_select_subdirectories(self):
        for start, stop in zip(range(49, -1, -1), range(49, 99)):
            with self.subTest(start=start, stop=stop):
                Project.create(self.drcty.name, start=start, stop=stop, quiet=True)
                self.assertEqual(
                    {"{0:02}".format(i) for i in range(start, stop + 1)},
                    set(os.listdir(self.drcty.name))
                )
