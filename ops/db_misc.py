
from .base import Op, Struct, String, Short, Int, Bytes, List, Long



class DBSize(Op):
    """Returns the database size in bytes"""
    op_type = 8

    class Request(Struct):
        pass

    class Response(Struct):
        size = Long()
    

class DBCountRecords(Op):
    """Returns the total number of records in the database"""
    op_type = 9

    class Request(Struct):
        pass

    class Response(Struct):
        count = Long()
