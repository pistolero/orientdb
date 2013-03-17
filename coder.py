import re
from decimal import Decimal

def odb_loads(x):
    decoder = RecordDecoder()
    return decoder.decode(x)


from .types import RID

class RecordDecoder(object):
    number_format_map = {
        'b': int,
        's': int,
        'l': long,
        'f': float,
        'd': float,
        'c': Decimal
    }
    def decode(self, raw):
        self.raw = raw
        self.view = buffer(raw)
        self.state_stack = []

        class_name = self.read_class()
        data = self.read_obj()
        return {'class': class_name, 'data': data}

    @property
    def isFinished(self):
        return len(self.view) == 0

    def push_state(self):
        self.state_stack.append(self.view)

    def restore_state(self):
        self.view = self.state_stack.pop()

    def pop_state(self):
        self.state_stack.pop()

    def read_class(self):
        self.push_state()

        class_name = self.read_word()
        if self.read_char() != '@':
            class_name = None
            self.restore_state()
        else:
            self.pop_state()
        return class_name

    def read_nested_obj(self):
        self.expect(re.compile('\('))
        return self.read_obj()

    def read_map(self):
        self.expect(re.compile('{'))
        result = {}
        while not self.isFinished:
            key=self.read_string()
            self.expect(re.compile(':'))

            val = self.read_value()
            result[key] = val

            if self.isFinished:
                break

            c = self.read_char()
            if c == ',':
                continue
            if c in ('}',):
                break
        return result

    def read_obj(self):
        result = {}
        while not self.isFinished:
            key=self.read_word()
            self.expect(re.compile(':'))

            val = self.read_value()
            result[key] = val

            if self.isFinished:
                break

            c = self.read_char()
            if c == ',':
                continue
            if c in (')', '}'):
                break
        return result
        #val=self.read_value()

    def read_word(self):
        return self.read(re.compile('(")?\w+(?(1)")'))

    def read_value(self):
        if self.isFinished:
            return None
        peek = self.peek_char()
        if peek in (',', ')', '}'):
            return None
        elif peek == '"':
            return self.read_string()
        elif peek == '[':
            return self.read_array()
        elif peek == '(':
            return self.read_nested_obj()
        elif peek == '{':
            return self.read_map()
        elif peek == '#':
            return self.read_rid()
        elif peek.isdigit():
            return self.read_number()
        elif peek == 'f':
            self.read(re.compile('false'))
            return False
        elif peek == 't':
            self.read(re.compile('false'))
            return True
        elif peek == 'n':
            self.read(re.compile('null'))
            return None
        else:
            raise ValueError('Unable to determine value type by first byte %r' % peek)

    def read_number(self):
        val = self.read(re.compile('\d+(\.\d+)?(\w)?'))
        format = int
        if not val[-1].isdigit():
            format = self.number_format_map[val[-1]]
            val = val[:-1]
            
        return format(val)

    def read_rid(self):
        self.expect(re.compile('#'))
        val = self.read(re.compile('\d+:\d+'))
        return RID(*map(int, val.split(':', 1)))

    def read_array(self):
        self.expect(re.compile('\['))
        result = []

        while True:
            if self.peek_char() == ']':
                self.read_char()
                break

            val = self.read_value()
            result.append(val)
            c = self.read_char()
            if c == ',':
                continue
            if c == ']':
                break
        return result

    def read_string(self):
        self.expect(re.compile('"'))
        result = self.read(re.compile('.*?"'))
        return unescape(result[:-1])
        
    def expect(self, re):
        val = self.read(re)
        if val is None:
            raise ValueError('Expected %s but got %s' % (re.pattern, val))

    def peek_char(self):
        return self.view[0]

    def read_char(self):
        result = self.view[0]
        self.view = self.view[1:]
        return result

    def read(self, re):
        m = re.match(self.view)
        if m:
            self.view = self.view[m.end():]
            return m.group(0)
        raise RuntimeError('Failed to parse %s. View is %r' % (re.pattern, self.view[:50]))


from .utils import StringIO

class RecordEncoder(object):
    def encode(self, record):
        self.buf = StringIO()

        self.write_class(record)
        self.write_data(record)

    def write_class(self, record):
        if record.class_name:
            self.buf.write(record.class_name)
            self.buf.write('@')

    def write_data(self, record):
        for key, value in record.data.iteritems():
            self.buf.write(key)
            self.buf.write(':')
            self.write_value(value)

    def write_value(self, value, explicit_null=False):
        if value is None and explicit_null:
            self.buf.write('null')
        elif isinstance(value, bool):
            self.buf.write('true' if value else 'false')
        elif isinstance(value, basestring):
            self.buf('')


_escape_re = re.compile(r'["\\]')
_unescape_re = re.compile(r'\\(["\\])')

def escape(s):
    # def replacer(match):
    #     if match.group(0) == '"':
    #         return r'\"'
    #     elif match.group(0) == '/':
    #         return r'\\'
    return _escape_re.sub('\\\\\g<0>', s)

def unescape(s):
    return _unescape_re.sub('\g<1>', s)