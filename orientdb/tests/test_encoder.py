from nose.tools import eq_
from orientdb import OClass, StringProperty, LinkListProperty, LinkProperty
from orientdb.coder import odb_dumps



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



def test_odb_dumps():
    ni1 = NodeInput('input1')
    n = Node(name='123', inputs=[ni1])

    real = odb_dumps(n)
    expected = ""

    eq_(real, expected)