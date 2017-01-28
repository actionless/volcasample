#!/usr/bin/env python3
# encoding: UTF-8

import os.path
import shutil
import tempfile
import unittest

import pkg_resources

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
        rv = Project.create(self.drcty.name, quiet=True)
        self.assertEqual(100, rv)
        self.assertEqual(
            {"{0:02}".format(i) for i in range(100)},
            set(os.listdir(self.drcty.name))
        )

    def test_select_subdirectories(self):
        for start, span in zip(range(49, -1, -1), range(1, 100)):
            with self.subTest(start=start, span=span):
                rv = Project.create(self.drcty.name, start=start, span=span, quiet=True)
                self.assertEqual(span, rv)
                self.assertEqual(
                    {"{0:02}".format(i) for i in range(start, start + span)},
                    set(os.listdir(self.drcty.name))
                )

class RefreshProjectTests(NeedsTempDirectory, unittest.TestCase):

    def setUp(self):
        super().setUp()
        self.assertEqual(2, Project.create(self.drcty.name, start=0, span=2, quiet=True))
        data = pkg_resources.resource_filename("volcasample.test", "data")
        for src, dst in zip(sorted(os.listdir(data)), ("00", "01")):
            rv = shutil.copy(os.path.join(data, src), os.path.join(self.drcty.name, dst))

    def test_refresh_no_history(self):
        rv = list(Project.refresh(self.drcty.name, quiet=True))
        for metadata in rv:
            self.assertTrue(all(i in metadata for i in (
                "path", "vote", "nchannels", "sampwidth"
            )))
            self.assertEqual(0, metadata["vote"])
            self.assertTrue(os.path.isfile(metadata["path"]))

    def test_select_refresh_no_history(self):
        rv = list(Project.refresh(self.drcty.name, start=0, span=1, quiet=True))
        self.assertEqual(1, len(rv))
        metadata = rv[0]
        self.assertTrue(all(i in metadata for i in (
            "path", "vote", "nchannels", "sampwidth"
        )))
        self.assertEqual(0, metadata["vote"])
        self.assertTrue(os.path.isfile(metadata["path"]))

    def test_refresh_with_history(self):
        with open(os.path.join(self.drcty.name, "00", "metadata.json"), "w") as history:
            history.write('{"vote": 16472}')
        rv = next(Project.refresh(self.drcty.name, quiet=True))
        self.assertEqual(16472, rv["vote"])
