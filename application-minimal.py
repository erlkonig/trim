#!/usr/bin/env python
# -*- encoding:utf-8 -*-

import argparse
import copy
import flask
import json
import re
import sqlalchemy
import sys

'''
Provide a REST service with a search URL to find all Vehicle Service Number
patterns in the database which match a given VSN.  The patterns are each
associated with specific vehicle details (possible several sets) which are
returned if any are found.
'''

def dict_clone_and_update(a_ro, b_ro):
    '''Return the composite of the two dicts without changing them.
    '''
    c_rw = copy.deepcopy(a_ro)
    c_rw.update(b_ro)
    return c_rw


def json_dumps_pretty(the_object, **kwargs):
    '''
    json.dumps() with a number of defaults already set for an indented,
    deterministically ordered, UTF-8 friendly, trailing-space-free result.

    Options are the same as those for json.dumps().
    '''
    defaults = {
        'encoding': 'UTF-8',
        'ensure_ascii': False,  # but with encoding UTF-8
        'indent': 4,
        'separators': (',', ': '),    # space only after :
        'sort_keys': True
        }
    return json.dumps(the_object,
                      **dict_clone_and_update(defaults, kwargs))


class log(object):
    @staticmethod
    def error(fmt, *args): sys.stderr.write(('ERROR: ' + fmt + '\n') % args)


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

blueprint = flask.Blueprint('vehicles_api', __name__)

@blueprint.route('/v1/search', methods=['GET'])
@blueprint.route('/v1/search/<vsn>', methods=['GET'])
def api_search_vsn(vsn=None):
    '''
    A basic search supporting these styles:

        http://..../api/vehicles/v1/search?vsn=ABCDEF123456
        http://..../api/vehicles/v1/search/ABCDEF123456

    Since a result set can be 0 or many entries, a 200 is returned for both.
    '''
    vehicles = Vehicles()
    result, status = {'message': 'go flog a developer'}, 500
    if not vsn:
        vsn = flask.request.args.get('vsn', None)

    try:
        print('VSN: %r' % (vsn,))
        if not vsn:
            result, status = {'message': 'No VSN provided'}, 400
        elif not vehicles.vsn_valid(vsn):
            result, status = {'message': 'Invalid VSN provided'}, 400
        else:
            result, status = vehicles.search_by_vsn(vsn), 200
    except Exception as e:  # I wonder if a decorator could be used for this
        log.error('Unhandled exception caught for VSN %r: %r' % (vsn, e))

    return json_dumps_pretty(result), status


def make_app():
    '''Create the Flask application.
    '''
    app = flask.Flask(__name__)
    app.config['JSON_AS_ASCII'] = False
    app.register_blueprint(blueprint, url_prefix='/api/vehicles')
    return app


def main(args):
    '''Argument parsing and firing up the Flash application.
    '''
    parser = argparse.ArgumentParser(description='HTTP server.')
    parser.add_argument('--port', type=int,  default=5000,
                        help='which port to listen on')
    parser.add_argument('--dsn', type=str,  default='sqlite:///database.sqlite',
                        help='DSN for where to find the database')
    args = parser.parse_args()
    app = make_app()
    app.run(host='0.0.0.0', port=args.port, debug=True)


if __name__ == '__main__':
    sys.exit(0 if main(sys.argv) else -1)

# vim: encoding=utf-8 sw=4 ts=4 sts=4 ai et sta
