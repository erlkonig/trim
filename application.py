#!/usr/bin/env python
# -*- encoding:utf-8 -*-

import argparse
import flask
import sys

import lib.vehicles.api as vehicles_api


def make_app():
    '''Create the Flask application.
    '''
    app = flask.Flask(__name__)
    app.config['JSON_AS_ASCII'] = False
    app.register_blueprint(vehicles_api.blueprint, url_prefix='/api/vehicles')
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
