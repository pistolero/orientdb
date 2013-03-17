import sys
import logging
import socket

from ops import *
from sock import OrientDBSocket, FullRecordData
from .types import RID, Document, create_record
from .classes import class_factory
PROTOCOL_VERSION = 13

class ODBServer(object):
    logger = logging.getLogger('orientdb.server')
    def __init__(self, host, port=2424):
        self.host = host
        self.port = port
        self._sock = None


    def connect(self):
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.connect((self.host, self.port))
        self._sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.socket = OrientDBSocket(self._sock)
        self.min_version = self.socket.read_short()

        assert self.min_version == PROTOCOL_VERSION

        self.zero_session = ODBSession(self.socket, -1, [])

    # @property
    # def sock(self):
    #     if self._sock is None:
    #         self.connect()
    #     return self._sock

    def open(self, db_name, db_type='document', username='admin', password='admin'):
        cmd = DBOpen(self.zero_session, database_name=db_name, database_type=db_type, username=username, password=password, protocol_version=PROTOCOL_VERSION)
        resp = cmd.send()

        # for c in resp.clusters:
        #     print c.cluster_name, c.cluster_id, c.cluster_type, c.cluster_data_segment

        return ODBSession(self.socket, resp.session_id, resp.clusters)


class ODBSession(object):
    def __init__(self, socket, session_id, clusters):
        self.socket = socket
        self.session_id = session_id
        self.clusters = clusters

        self.identityMap = {}
        self.new = set()
        self.deleted = set()
        self.modified = set()

    @property
    def db_size(self):
        cmd = DBSize(self)
        resp = cmd.send()
        return resp.size

    @property
    def num_records(self):
        cmd = DBCountRecords(self)
        resp = cmd.send()
        return resp.count

    def get_record(self, rid):
        if rid in self.identityMap:
            return self.identityMap[rid]
        return self.load_record(rid)

    def load_record(self, rid, fetch_plan='*:0'):
        logging.debug('Loading record %r', rid)
        cmd = RecordLoad(self, cluster_id=rid.cluster_id, cluster_position=rid.position, fetch_plan=fetch_plan)
        resp = cmd.send()

        result = None

        for data in resp.records:
            assert data.record_type == ord('d')

            if isinstance(data, PartialRecordData):
                record_rid = rid
            else:
                record_rid = data.rid

            if record_rid in self.identityMap:
                continue

            rec = create_record(self, data.record_type, record_rid, data.version, data.content, class_factory)

            if result is None:
                result = rec

            self.identityMap[record_rid] = rec

        return result

    def commit(self):
        ops = []
        id_generator = iter(xrange(-2, -sys.maxint, -1))
        obj_map = {}
        content = MemoryWriter()
        for obj in self.new:
            obj.position = id_generator.next()
            obj.serialize(content)
            ops.append(CreateOp(content=content.reset()))
            obj_map[obj.rid] = obj
        for obj in self.modified:
            obj.serialize(content)
            obj.append(UpdateOp(original_version=obj.version,
                content=content.reset()))
            obj_map[obj.rid] = obj
        for obj in self.deleted:
            obj.append(DeleteOp(original_version=obj.version))

        if not ops:
            return

        cmd = TxCommit(self, tx_id=1, use_tx_log=1, record_ops=ops)
        resp = cmd.send()

        for c in resp.created:
            print c
            obj = obj_map[RID(c.client_specified_cluster_id, c.client_specified_position)]
            obj.cluster_id = c.created_cluster_id
            obj.position = c.created_position

        for u in resp.updated:
            obj = obj_map[RID(u.updated_cluster_id, u.updated_position)]
            obj.version = u.new_record_version

        self.new.clear()
        self.modified.clear()
        self.deleted.clear()



if __name__ == '__main__':
    server = ODBServer('127.0.0.1')
    server.connect()
    session = server.open('ls')
    #session = server.session()
    x = session.load_record(10, 1, fetch_plan='*:0')
    print x
    print x.inputs[0]
    #print session.identityMap
    # d=Document(rid=RID(10,-1))
    # session.new.add(d)
    # session.commit()
    # print d.rid
    #print session.num_records