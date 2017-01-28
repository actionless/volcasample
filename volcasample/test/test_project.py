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

class CopiesTestData(NeedsTempDirectory):

    def setUp(self):
        super().setUp()
        self.assertEqual(2, Project.create(self.drcty.name, start=0, span=2, quiet=True))
        data = pkg_resources.resource_filename("volcasample.test", "data")
        for src, dst in zip(sorted(os.listdir(data)), ("00", "01")):
            rv = shutil.copy(os.path.join(data, src), os.path.join(self.drcty.name, dst))

class ProjectCreateTests(NeedsTempDirectory, unittest.TestCase):

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

class ProjectRefreshTests(CopiesTestData, unittest.TestCase):

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

class ProjectVoteTests(CopiesTestData, unittest.TestCase):

    def test_vote_single_value(self):
        rv = next(Project.vote(self.drcty.name, val=16472, start=0, span=1, quiet=True))
        self.assertEqual(16472, rv["vote"])

    def test_vote_many_value(self):
        rv = list(Project.vote(self.drcty.name, val=16472, start=0, span=2, quiet=True))
        self.assertTrue(all(i["vote"] == 16472 for i in rv))
        self.assertEqual(2, len(rv))

    def test_vote_single_positive_increment(self):
        list(Project.vote(self.drcty.name, val=16472, start=0, span=1, quiet=True))
        rv = next(Project.vote(self.drcty.name, incr=2, start=0, span=1, quiet=True))
        self.assertEqual(16474, rv["vote"])

    def test_vote_single_negative_increment(self):
        list(Project.vote(self.drcty.name, val=16472, start=0, span=1, quiet=True))
        rv = next(Project.vote(self.drcty.name, incr=-2, start=0, span=1, quiet=True))
        self.assertEqual(16470, rv["vote"])

    def test_vote_many_positive_increment(self):
        list(Project.vote(self.drcty.name, val=16472, start=0, span=2, quiet=True))
        rv = list(Project.vote(self.drcty.name, incr=2, start=0, span=2, quiet=True))
        self.assertTrue(all(i["vote"] == 16474 for i in rv))
        self.assertEqual(2, len(rv))

    def test_vote_many_negative_increment(self):
        list(Project.vote(self.drcty.name, val=16472, start=0, span=2, quiet=True))
        rv = list(Project.vote(self.drcty.name, incr=-2, start=0, span=2, quiet=True))
        self.assertTrue(all(i["vote"] == 16470 for i in rv))
        self.assertEqual(2, len(rv))
