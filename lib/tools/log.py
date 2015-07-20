# -*- encoding:utf-8 -*-

'''
A class to ease later replacement with something more sophisticated.
'''

class log(object):
    '''
    Log an error message using a severity level.
    Typically this would be imported as:

       from lib.tools.log import log

    to allow log.error() and so on to be used simply.
    '''
    @staticmethod
    def error(fmt, *args):
        '''Log with ERROR severity.'''
        sys.stderr.write(('ERROR: ' + fmt + '\n') % args)

# vim: encoding=utf-8 sw=4 ts=4 sts=4 ai et sta
