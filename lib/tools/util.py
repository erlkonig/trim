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


# vim: encoding=utf-8 sw=4 ts=4 sts=4 ai et sta
