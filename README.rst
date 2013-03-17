OrientDB
========

Pure Python OrientDB binary protocol adapter and Object to Graph mapper
for `OrientDB`_ database.

**work-in-progress, use at own risk.**

**so far it has support only for reading objects from OrientDB**


Usage example:

.. code:: python

    from orientdb import OClass, StringProperty, LinkListProperty, LinkProperty, ODBServer

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

    server = ODBServer('127.0.0.1') 
    server.connect() 
    session = server.open('somedb') 
    x = session.load_record(RID(11, 4), fetch_plan='\*:0') 
    print x print x.\_\_dict\_\_ 
    print x.node
    print x.node.inputs 
    print x.node.inputs[0:3]


.. _OrientDB: http://www.orientdb.org/