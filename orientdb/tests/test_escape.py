from nose.tools import eq_
from orientdb.coder import escape, unescape


def escape_test():

    real = escape('asdf"g\\h')
    expected = 'asdf\\"g\\\\h'

    eq_(real, expected)



def unescape_test():
    real = unescape('asdf\\"g\\\\h')
    expected = 'asdf"g\\h'

    eq_(real, expected)

