# -*- encoding:utf-8 -*-

import flask
import json
import lib.tools.util as lib_util
import lib.vehicles as lib_vehicles


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
    vehicles = lib_vehicles.Vehicles()
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

    return lib_util.json_dumps_pretty(result), status


# vim: encoding=utf-8 sw=4 ts=4 sts=4 ai et sta

