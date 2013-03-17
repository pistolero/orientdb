import struct

from .utils import MemoryWriter
from .types import RID


def _make_read(name, tpl):
    size = struct.calcsize(tpl)
    def func(self):
        bytes = self._recv(size)
        return struct.unpack(tpl, bytes)[0]
    func.__name__ = 'read_%s' % name
    return func


class OrientDBSocket(object):
    #logger = logging.getLogger('OrientDB.socket')
    def __init__(self, sock):
        self.sock = sock
        self.writer = MemoryWriter()

        # copy methods from writer
        for key in dir(self.writer):
            if not key.startswith('write'):
                continue
            setattr(self, key, getattr(self.writer, key))

    def flush(self):
        self.sock.sendall(self.writer.reset())
        # self.sock.sendall(self.buf.getvalue())
        # self.buf.seek(0)
        # self.buf.truncate()

    read_byte = _make_read('byte', '>b')
    read_short = _make_read('short', '>h')
    read_int = _make_read('int', '>i')
    read_long = _make_read('long', '>q')

    def read_bytes(self):
        strlen = self.read_int()
        if strlen == -1:
            return None
        if strlen == 0:
            return ''
        return self._recv(strlen)

    def read_string(self):
        s = self.read_bytes()
        if s is not None:
            return s.decode('utf-8')
        return s

    def read_record(self):
        record_type = self.read_short()
        if record_type == -2:
            return None
        elif record_type == -3:
            cluster_id = self.read_short()
            position = self.read_long()
            return RID(cluster_id, position)
        elif record_type == 0:
            record_type = self.read_byte()
            cluster_id = self.read_short()
            position = self.read_long()
            version = self.read_int()
            content = self.read_bytes()
            return FullRecordData(record_type, RID(cluster_id, position), version, content)
        else:
            raise ValueError('Don\'t know how to read record with type %d' % record_type)

    def _recv(self, bytes):
        bytes_left = bytes
        buf = []
        while bytes_left:
            chunk = self.sock.recv(bytes_left)
            if not chunk:
                raise IOError('Failed to read %d bytes' % bytes)
            bytes_left -= len(chunk)
            buf.append(chunk)
        result = ''.join(buf)

        # for c in result:
        #     print '%02x' % ord(c),
        # print
        # print repr(result)

        return result




class FullRecordData(object):
    def __init__(self, record_type, rid, version, content):
        self.record_type = record_type
        self.rid = rid
        self.version = version
        self.content = content

    def __repr__(self):
        return 'FullRecordData(%r, %r, %r, %r)' % (self.record_type, self.rid, self.version, self.content)

