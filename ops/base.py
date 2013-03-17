

class Attr(object):

    creation_counter = 0

    def __init__(self, default=None):
        self.name = None
        self.creation_counter = Attr.creation_counter
        Attr.creation_counter += 1
        self.default = default

    def __get__(self, instance, owner):
        if self.name not in instance.__dict__:
            val = self.default
            if callable(val):
                val = val
            instance.__dict__[self.name] = val
        else:
            val = instance.__dict__[self.name]

        return val


    def __set__(self, instance, value):
        instance.__dict__[self.name] = value


class StructMeta(type):
    def __new__(cls, class_name, bases, dct):


        fields = [(name, value) for name, value in dct.items() if isinstance(value, Attr)]
        fields.sort(key=lambda x:x[1].creation_counter)

        for name, attr in fields:
            attr.name = name

        def write_to(x, sock):
            for field_name, field_attr in fields:
                field_attr.write_to(sock, getattr(x, field_name))

        write_to.__name__ == 'write_to_%s' % class_name
        dct['write_to'] = write_to


        def read_from(cls, reader):
            kw = dict()
            for field_name, field_attr in fields:
                val = field_attr.read(reader)
                kw[field_name] = val

            return cls(**kw)
        dct['read_from'] = classmethod(read_from)

        def repr(self):
            bits = []
            for field_name, attr in fields:
                bits.append('%s=%r' % (field_name, getattr(self, field_name, None)))
            return '%s(%s)' % (class_name, ', '.join(bits))
        dct['__repr__'] = repr


        return super(StructMeta, cls).__new__(cls, class_name, bases, dct)


class Struct(object):
    __metaclass__ = StructMeta

    def __init__(self, **kw):
        for key, val in kw.items():
            setattr(self, key, val)


class Byte(Attr):
    def write_to(self, sock, value):
        sock.write_byte(value)

    @classmethod
    def read(cls, reader):
        return reader.read_byte()


class Short(Attr):        
    def write_to(self, sock, value):
        sock.write_short(value)

    @classmethod
    def read(cls, reader):
        return reader.read_short()


class String(Attr):
    def write_to(self, sock, value):
        sock.write_string(value)

    @classmethod
    def read(cls, reader):
        return reader.read_string()


class Bytes(Attr):
    def write_to(self, sock, value):
        sock.write_bytes(value)

    @classmethod
    def read(cls, reader):
        return reader.read_bytes()


class Int(Attr):
    def write_to(self, sock, value):
        sock.write_int(value)

    @classmethod
    def read(cls, reader):
        return reader.read_int()


class Long(Attr):
    def write_to(self, sock, value):
        sock.write_long(value)

    @classmethod
    def read(cls, reader):
        return reader.read_long()


class BaseList(Attr):
    def __init__(self):
        super(BaseList, self).__init__()


class List(BaseList):    
    def __init__(self, struct):
        super(List, self).__init__()
        self.struct = struct
        self._value = []

    def write_to(self, sock):
        sock.write_short(len(self.value))
        for v in self.value:
            v.write_to(sock)

    def read(self, reader):
        result = []
        total = reader.read_short()
        for i in range(total):
            obj = self.struct.read_from(reader)
            result.append(obj)

        return result


class IntList(BaseList):    
    def __init__(self, struct):
        super(IntList, self).__init__()
        self.struct = struct
        self._value = []

    def write_to(self, sock):
        sock.write_int(len(self.value))
        for v in self.value:
            v.write_to(sock)

    def read(self, reader):
        result = []
        total = reader.read_int()
        for i in range(total):
            obj = self.struct.read_from(reader)
            result.append(obj)

        return result



class ChainedList(Attr):    
    def __init__(self, struct):
        super(ChainedList, self).__init__()
        self.struct = struct

    def write_to(self, sock):
        raise NotImplementedError()
        # sock.write_short(len(self.value))
        # for v in self.value:
        #     v.write_to(sock)

    def read(self, reader):
        result = []
        status = reader.read_byte()
        if status != 0:
            obj = self.struct.read_from(reader)
            obj.status = status
            result.append(obj)
            status = reader.read_byte()

        while status != 0:
            rec = reader.read_record()
            result.append(rec)
            status = reader.read_byte()

        return result





class Op(object):
    async = False

    def __init__(self, session, **kw):
        self.session = session
        self.req = self.Request(**kw)

    def send(self):
        sock = self.session.socket
        sock.write_byte(self.op_type)
        sock.write_int(self.session.session_id)
        self.req.write_to(sock)
        sock.flush()

        if not self.async:
            result = sock.read_byte()
            if result == 1:
                raise RuntimeError('OrientDB error')

            session_id = sock.read_int()
            assert session_id == self.session.session_id
            return self.Response.read_from(sock)
