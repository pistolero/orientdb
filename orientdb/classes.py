import new

class ClassProperty(object):
    name = None

    def __get__(self, instance, klass=None):
        return instance.__dict__[self.name]

    def __set__(self, instance, value):
        instance.__dict__[self.name] = value


class OClassFactory(object):
    def __init__(self):
        self.classes = {}
        self.generated_classes = {}

    def register(self, klass):
        self.classes[klass.__classname__] = klass

    def create(self, session, class_name, **data):
        if class_name in self.classes:
            klass = self.classes[class_name]
        elif class_name in self.generated_classes:
            klass = self.generated_classes[class_name]
        else:
            klass = self.generate_class(class_name)
        return klass(_session=session, **data)

    def generate_class(self, class_name):
        def repr(self):
            return 'Generated%sClass' % class_name
        klass = new.classobj(class_name, (OClass, ), {'__repr__': repr})
        self.generated_classes[class_name] = klass
        return klass


class_factory = OClassFactory()


class ClassMeta(type):
    def __new__(cls, class_name, bases, dct):

        fields = dict([(name, value) for name, value in dct.items() if isinstance(value, ClassProperty)])
        # fields.sort(key=lambda x:x[1].creation_counter)
        for name, field in fields.items():
            field.name = name
        dct['_fields'] = fields


        # define classname
        if '__classname__' not in dct:
            dct['__classname__'] = class_name


        kls = super(ClassMeta, cls).__new__(cls, class_name, bases, dct)
        class_factory.register(kls)
        return kls


class DynamicProperty(ClassProperty):
    pass

class StringProperty(ClassProperty):
    pass

class IntField(ClassProperty):
    pass

class Boolean(ClassProperty):
    pass

class LinkProperty(ClassProperty):
    def __init__(self, type):
        self.type = type

    def __get__(self, instance, klass=None):
        val = instance.__dict__[self.name]
        
        if isinstance(val, RID):
            val = instance._session.get_record(val)
        return val
        # rid = instance.__dict__[self.name]
        # return instance._session.load_record(rid)

    def __set__(self, instance, value):
        if not isinstance(value, (self.type, RID)):
            raise ValueError('%s accepts only instances of %r' % (self.name, self.type))
        instance.__dict__[self.name] = value
        # if isinstance(value, RID):
        #     rid = value
        # else:
        #     rid = value.id
        # instance.__dict__[self.name] = Link(rid, instance._session)


from .types import RID
class Link(object):
    def __init__(self, rid, session):
        self.__rid = rid
        self.__session = session
        self.__obj = None

    def __getattr__(self, name):
        if self.__obj is None:
            self.__obj = self.__session.load_record(self.__rid)
        return getattr(self.__obj, name)


class Date(ClassProperty):
    pass

class Binary(ClassProperty):
    pass

class EmbeddedDocumentField(ClassProperty):
    pass

class Set(ClassProperty):
    pass

class List(ClassProperty):
    def __init__(self, type):
        self.type = type

    def __getattr__(self, instance, klass=None):
        pass

class LinkListProperty(ClassProperty):
    def __set__(self, instance, value):
        if not isinstance(value, list):
            raise ValueError()

        if not isinstance(value, LinkList):
            value = LinkList(instance, value)
        instance.__dict__[self.name] = value


class LinkList(object):
    def __init__(self, instance, list):
        self._instance = instance
        self._list = list

    def __getitem__(self, key):
        val = self._list[key]
        if isinstance(val, RID):
            return self._instance._session.get_record(val)
        elif isinstance(key, slice):
            return [self._instance._session.get_record(x) for x in val]
        return val

    def __setitem__(self, key, val):
        self._list[key] = val
        self._instance.markAsDirty()

    def __repr__(self):
        return 'LinkList(%s)' % super(LinkList, self).__repr__()


class Map(ClassProperty):
    pass
    

from .types import Document
class OClass(Document):
    __metaclass__ = ClassMeta

    def __init__(self, _session=None, **kw):
        self._session = _session
        for key, val in kw.iteritems():
            setattr(self, key, val)
