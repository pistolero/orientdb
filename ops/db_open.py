from ..version import __version__

from .base import Op, Struct, String, Short, Int, Bytes, List


class ClusterInfo(Struct):
    cluster_name = String()
    cluster_id = Short()
    cluster_type = String()
    cluster_data_segment = Short()


class DBOpen(Op):
    op_type = 0x3

    class Request(Struct):
        driver_name = String(default='Python OrientDB driver')
        driver_version = String(default=__version__)
        protocol_version = Short()
        client_id = String(default='')
        database_name = String()
        database_type = String()
        username = String()
        password = String()

    class Response(Struct):
        session_id = Int()
        clusters = List(ClusterInfo)
        cluster_config = Bytes()
        #orientdb_release = String()
    