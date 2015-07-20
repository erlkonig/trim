#!/usr/bin/env python
# -*- coding: utf-8 -*-

import copy
import json
import requests
import sys
import unittest

'''
Tests for REST calls.'
'''

class TestRestVsnSearches(unittest.TestCase):
    '''Tests for VSN searches.
    '''
    def setUp(self):
        '''Set the base URL used for tests.
        '''
        self.url_base = 'http://127.0.0.1:5000/'

    def url(self, suburl):
        '''Return the catentation of the base URL and a suburl.
        '''
        return self.url_base + suburl

    def test_vsn_url_missing_arg(self):
        '''Complain if .../search/ form lacks its VSN.
        '''
        suburls = ['api/vehicles/v1/search/']
        for url in map(self.url, suburls):
            r = requests.get(url)
            self.assertEqual(404, r.status_code)

    def test_vsn_missing(self):
        '''Complain on missing VSN.
        '''
        suburls = ['api/vehicles/v1/search',
                   'api/vehicles/v1/search?',
                   'api/vehicles/v1/search?vsn',
                   'api/vehicles/v1/search?vsn=']
        for url in map(self.url, suburls):
            r = requests.get(url)
            self.assertEqual(400, r.status_code)
            obj = json.loads(r.text)
            self.assertEqual({"message": "No VSN provided"}, obj)

    def test_vsn_invalid(self):
        '''Complain on invalid VSN
        '''
        suburls = ['api/vehicles/v1/search/tooshort',
                   'api/vehicles/v1/search/waytoooooooooooolong',
                   'api/vehicles/v1/search/ABCDE1F23456',  # mixed dig/letter
                   'api/vehicles/v1/search/123456ABCDEF',  # swappend ends
                   'api/vehicles/v1/search/abcdef123456',  # lowercase
                   'api/vehicles/v1/search/ABCDEF123DEF',  # hex digits
                   'api/vehicles/v1/search/ABCDE123456',   # one letter missing
                   'api/vehicles/v1/search/ABCDEF12345',   # one digit missing
                   ]
        for url in map(self.url, suburls):
            r = requests.get(url)
            self.assertEqual(400, r.status_code)
            obj = json.loads(r.text)
            self.assertEqual({"message": "Invalid VSN provided"}, obj)

    def test_vsn_finds_none(self):
        '''Verify searches can return [].
        '''
        suburls = ['api/vehicles/v1/search/NOSUCH123456',
                   'api/vehicles/v1/search?vsn=NOSUCH123456']
        for url in map(self.url, suburls):
            r = requests.get(url)
            self.assertEqual(200, r.status_code)
            obj = json.loads(r.text)
            self.assertEqual([], obj)

    def test_vsn_finds_single(self):
        '''Verify search can return a list of one.
        '''
        suburls = ['api/vehicles/v1/search/XXRCIV077030',
                   'api/vehicles/v1/search?vsn=XXRCIV077030']
        for url in map(self.url, suburls):
            r = requests.get(url)
            self.assertEqual(200, r.status_code)
            obj = json.loads(r.text)
            self.assertEqual(
                [{
                    "make": "Volkswagen",
                    "match_strength": 0,
                    "model": "GTI",
                    "trim_id": "253905",
                    "trim_name": "2-Door with Convenience and Sunroof, DSG",
                    "vsn_pattern": "XXRC*V****3*",
                    "year": "2013"
                }],
                obj)

    def test_vsn_finds_several(self):
        '''Verify search can return a list of several.
        '''
        suburls = ['api/vehicles/v1/search/XXRCIV077000',
                   'api/vehicles/v1/search?vsn=XXRCIV077000']
        for url in map(self.url, suburls):
            r = requests.get(url)
            self.assertEqual(200, r.status_code)
            obj = json.loads(r.text)
            self.assertEqual([
                {
                    "make": "Volkswagen",
                    "match_strength": 0,
                    "model": "GTI",
                    "trim_id": "253909",
                    "trim_name": "2-Door with Sunroof and Navigation, DSG",
                    "vsn_pattern": "XXRC*V******",
                    "year": "2013"
                },
                {
                    "make": "Volkswagen",
                    "match_strength": 0,
                    "model": "GTI",
                    "trim_id": "253901",
                    "trim_name": "2-Door DSG",
                    "vsn_pattern": "XXRC*V******",
                    "year": "2013"
                },
                {
                    "make": "Volkswagen",
                    "match_strength": 0,
                    "model": "GTI",
                    "trim_id": "253913",
                    "trim_name": "2-Door Autobahn, DSG",
                    "vsn_pattern": "XXRC*V******",
                    "year": "2013"
                }],
                obj)


# vim: encoding=utf-8 sw=4 ts=4 sts=4 ai et sta
