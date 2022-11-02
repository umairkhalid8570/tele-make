# -*- coding: utf-8 -*-
# Part of Tele. See LICENSE file for full copyright and licensing details.

from unittest import TestCase

from tele.tests import MetaCase


class TestTestSuite(TestCase, metaclass=MetaCase):

    def test_test_suite(self):
        """ Check that TeleSuite handles unittest.TestCase correctly. """
