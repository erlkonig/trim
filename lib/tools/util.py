# -*- encoding:utf-8 -*-

import copy
import flask
import json

'''
Utility functions.'
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


def jsonic_by_accept_encoding(request,    # a flask.request
                              python_object,
                              *args, **kwargs):
    '''
    This method supports a Accept:application/json (for a rather compact
    JSON) or defaults to text/plain for human use.

    If using the "requests" module, the request.get(...) call would need
    this for JSON form:

       headers={'Accept':'application/json'}

    Curl would need:

       curl -H 'Accept: application/json' ...
    '''
    accept_content  = request.headers.get('Accept', 'text/plain')
    accept_encoding = request.headers.get('Accept-Encoding', 'identity')
    text = None

    if 'application/json' in accept_content:
        text = json.dumps(python_object)
        mimetype = 'application/json'
    else:    # elif accept_content in text/plain
        text = json_dumps_pretty(python_object)
        mimetype = 'text/plain'

    # Unicode non-BMP glyphs should be converted to surrogate pairs, but aren't
    return flask.current_app.response_class(text.encode('utf-8'),
                                            mimetype=mimetype)

# vim: encoding=utf-8 sw=4 ts=4 sts=4 ai et sta
