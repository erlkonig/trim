#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import sqlalchemy

from pprint import pprint as pp

'''
Handling of vehicle information.  This class is a bit reluctant to use,
say, sqlalchemy's full object model in order to avoid tying the two together.
This is based on the common observation that backends get swapped out a
lot.  In many cases, abstracting the database away entirely to a Database
class or the like to hide such detail is worthwhile.
'''

class Vehicles(object):
    '''
    Wrapper around a table with fields:
    { vsn_pattern trim_id year make model trim_name }
      str         int     int  str  str   str
    '''
    def __init__(self, table='vehicles'):
        '''
        A more fully featured version of this would pick up the database
        info from passed-in arguments from the api_* methods, which
        would be the nearest ones aware of Flask.
        '''

        self.db = sqlalchemy.create_engine('sqlite:///database.sqlite')
        self.db_metadata = sqlalchemy.MetaData(self.db)
        self.db_vehicles = sqlalchemy.Table('vehicles',
                                            self.db_metadata,
                                            autoload=True)
    @classmethod
    def vsn_valid(cls, vsn):
        return re.match('^[A-Z]{6}[0-9]{6}$', vsn) is not None

    @classmethod
    def vsn_pattern_valid(cls, vsn_pattern):
        return re.match('^[A-Z*]{6}[0-9*]{6}$', vsn) is not None

    @classmethod
    def vsn_match(cls, vsn, vsn_pattern):
        '''See if a VSN and a VSN pattern match.  Inferior to in-database SQL.
        '''
        match_strength = 0
        if cls.vsn_valid(vsn) and (len(vsn) == len(vsn_pattern)):
            # construct all paired positions, dropping those with wildcards
            pairs = filter(lambda pair: pair[1] != '*', zip(vsn, vsn_pattern))
            if pairs:    # each remaining pair must be twinned items, to match
                match_checks = map(lambda pair: pair[0] == pair[1], pairs)
                if all(match_checks):
                    match_strength = len(match_checks)
        return match_strength

    def search_by_vsn(self, vsn):
        # starting with the absolutely worst non-insane approach
        sql = self.db_vehicles.select()
        rows = sql.execute()
        matches = []
        match_strength_max_found = 0
        for row in rows:
            match_strength = self.vsn_match(vsn, row[0])
            if match_strength > 0:
                matches.insert(0, (match_strength, list(row)))
                if match_strength_max_found < match_strength:
                    match_strength_max_found = match_strength

        return [dict(zip(rows.keys() + ['match_strength'],
                         match[1] + [match_strength])) for match in matches
                if match[0] == match_strength_max_found]


# vim: encoding=utf-8 sw=4 ts=4 sts=4 ai et sta
