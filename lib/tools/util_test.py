#!/usr/bin/env python
# -*- coding: utf-8 -*-

import copy
import unittest

import lib.tools.util as util

'''
Tests for Utility functions.'
'''

class TestDictTools(unittest.TestCase):
    '''Tests for dictionary functions.
    '''
    def test_dict_clone_and_update(self):
        a = {"a": 1, "b": 2}
        b = {"b": 22, "c": 3}
        expected = {"a": 1, "b": 22, "c": 3}
        self.assertEqual(expected,
                         util.dict_clone_and_update(a, b))

class TestJson(unittest.TestCase):
    '''Tests for JSON functions.
    '''
    def test_json_dumps_pretty(self):
        pythonic = {
            "b": 42,
            "a": ['this', 'is', 'a', 'test']
        }
        expected = u'''{
    "a": [
        "this",
        "is",
        "a",
        "test"
    ],
    "b": 42
}'''
        self.assertEqual(expected, util.json_dumps_pretty(pythonic))


# vim: encoding=utf-8 sw=4 ts=4 sts=4 ai et sta

