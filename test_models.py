from .classes import OClass, StringProperty, LinkProperty, LinkListProperty
from .orientdb import ODBServer, RID

class Node(OClass):
    name = StringProperty()
    inputs = LinkListProperty()

    def __repr__(self):
        return 'Node(%r)' % self.name

class NodeInput(OClass):
    name = StringProperty()
    node = LinkProperty(Node)

    def __repr__(self):
        return 'NodeInput(%r)' % self.name

def test1():
    server = ODBServer('127.0.0.1')
    server.connect()
    session = server.open('ls')
    #session = server.session()
    x = session.load_record(RID(11, 4), fetch_plan='*:0')
    print x
    print x.__dict__
    print x.node

    print x.node.inputs
    print x.node.inputs[0:3]

