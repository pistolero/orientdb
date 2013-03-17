import struct
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO


from .types import RID


def _make_write(name, tpl):
    def func(self, x):
        try:
            self.buf.write(struct.pack(tpl, x))
        except struct.error:
            raise ValueError('Unable to write_%s with %r' % (name, x))
    func.__name__ = 'write_%s' % name        
    return func


class MemoryWriter(object):
    def __init__(self):
        self.buf = StringIO()

    def write_boolean(self, x):
        self.write_byte(1 if x else 0)

    write_byte = _make_write('byte', '>b')
    write_short = _make_write('short', '>h')
    write_int = _make_write('int', '>i')
    write_long = _make_write('long', '>q')
    write_byte = _make_write('byte', '>b')
    write_byte = _make_write('byte', '>b')
    write_byte = _make_write('byte', '>b')

    def write_bytes(self, x):
        if x is None:
            self.write_int(-1)
        else:
            self.write_int(len(x))
            self.buf.write(x)

    def write_string(self, x):
        if x is not None:
            x = x.encode('utf-8')
        self.write_bytes(x)

    def write_record(self, rec):
        if rec is None:
            self.write_short(-2)
        elif isinstance(rec, RID):
            self.write_short(-3)
            self.write_short(rec.cluster_id)
            self.write_long(rec.position)
        else:
            self.write_short(0)
            self.buf.write(rec.serialize())

    def write_strings(self, stringlist):
        self.write_int(len(stringlist))
        for s in stringlist:
            self.write_string(s)   

    def reset(self):
        value = self.buf.getvalue()
        self.buf.seek(0)
        self.buf.truncate()
        return value

