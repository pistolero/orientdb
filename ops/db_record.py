from ..version import __version__

from .base import Op, Struct, String, Short, Int, Bytes, List, Long, Byte, ChainedList



class PartialRecordData(Struct):
    content = Bytes()
    version = Int()
    record_type = Byte()
    #status_cache = Byte()


class RecordLoad(Op):
    op_type = 30

    class Request(Struct):
        cluster_id = Short()
        cluster_position = Long()
        fetch_plan = String()
        ignore_cache = Byte(default=0)
        tombstone = Byte(default=0)

    class Response(Struct):
        records = ChainedList(PartialRecordData)
