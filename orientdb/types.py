from collections import namedtuple


class RID(namedtuple('RID', ['cluster_id', 'position'])):
    def __repr__(self):
        return 'RID(%r, %r)' % (self.cluster_id, self.position)


class Record(object):
    TYPE = None
    def __init__(self, session, raw_data='', rid=None, version=-1):
        self._session = session
        if rid is None:
            self.rid = RID(-1, 01)
        else:
            self.rid = rid
        self.raw_data = raw_data
        self.version = version

    def serialize(self, sock):
        sock.write_byte(self.TYPE)
        sock.write_short(self.rid.cluster_id)
        sock.write_long(self.rid.position)
        sock.write_int(self.version)

        self.serialize_content(sock)

    def serialize_content(self, sock):
        sock.write(self.raw_data)

    @classmethod
    def create(kls, session, raw_data, rid, version, class_factory):
        return kls(session, raw_data, rid, version)


class Flat(Record):
    TYPE = ord('f')



###
from .coder import odb_loads


class Document(Record):
    TYPE = ord('d')

    def __init__(self, **kw):
        self.__dict__.update(kw)

    def serialize_content(self, sock):
        sock.write_bytes(self.raw_data)

    @classmethod
    def create(kls, session, raw_data, rid, version, class_factory):
        data = odb_loads(raw_data)
        class_name = data.get('class')
        if class_name:
            obj = class_factory.create(session, class_name, **data['data'])
        else:
            obj = kls(**data['data'])
        obj.rid = rid
        obj.version = version
        return obj



# class RIDProxy(object):
#     def __init__(self, session, rid):
#         self.rid = rid
#         self._record = None

#     def __getattr__(self, name):
#         if hasattr(name, self.rid):
#             return getattr(self.rid, name)
#         if self._record is None:
#             self._record = self.session.identityMap.get(self.rid)
#             if self._record is None:
#                 self._record = self.session.load_record(self.rid.cluster_id, self.rid.position)
#         return getattr(self._record, name)


def create_record(session, type, rid, version, raw_data, class_factory):
    klass = record_class_by_type(type)
    return klass.create(session, raw_data, rid, version, class_factory)


def record_class_by_type(type):
    if type == ord('d'):
        return Document
    elif type == ord('f'):
        return Flat
