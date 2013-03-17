from ..version import __version__

from .base import Op, Struct, String, Short, Int, Bytes, BaseList, Long, Byte, ChainedList, IntList


class CreateOp(Struct):
    content = Bytes()

class UpdateOp(Struct):
    original_version = Int()
    content = Bytes()

class DeleteOp(Struct):
    original_version = Int()


class OpList(BaseList):
    def write_to(self, sock, value):
        for op in value:
            if isinstance(op, CreateOp):
                sock.write_byte(3)
                op.write_to(sock)
            elif isinstance(op, UpdateOp):
                sock.write_byte(1)
                op.write_to(sock)
            elif isinstance(op, DeleteOp):
                sock.write_byte(2)
                op.write_to(sock)
            else:
                raise ValueError('Unknown operation %r' % op)
        sock.write_byte(0)

    def read(self, sock):
        raise NotImplementedError()


class CreatedInfo(Struct):
    client_specified_cluster_id = Short()
    client_specified_position = Long()

    created_cluster_id = Short()
    created_position = Long()

class UpdatedInfo(Struct):
    updated_cluster_id = Short()
    updated_position = Long()
    new_record_version = Int()


class TxCommit(Op):
    op_type = 60

    class Request(Struct):
        tx_id = Int()
        use_tx_log = Byte()
        record_ops = OpList()

    class Response(Struct):
        created = IntList(CreatedInfo)
        updated = IntList(UpdatedInfo)
