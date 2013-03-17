from nose.tools import eq_
from orientdb.coder import odb_loads, RID

#print odb_loads('ORole@name:"reader",inheritedRole:,mode:0,rules:{"database":2,"database.cluster.internal":2,"database.cluster.orole":2,"database.cluster.ouser":2,"database.class.*":2,"database.cluster.*":2,"database.query":2,"database.command":2,"database.hook.record":2}')

def test_odb_loads1():
    source = 'Profile@nick:"ThePresident",follows:[],followers:[#10:5,#10:6],name:"Barack",surname:"Obama",location:#3:2,invitedBy:,salary_cloned:,salary:120.3f'

    result = odb_loads(source)
    expected = {'data': {'salary': 120.3, 'surname': 'Obama', 'name': 'Barack', 'follows': [], 'salary_cloned': None, 'nick': 'ThePresident', 'followers': [RID(10, 5), RID(10, 6)], 'location': RID(3, 2), 'invitedBy': None}, 'class': 'Profile'}

    eq_(result, expected)


def test_odb_loads2():
    source = 'name:"ORole",id:0,defaultClusterId:3,clusterIds:[3],properties:[(name:"mode",type:17,offset:0,mandatory:false,notNull:false,min:,max:,linkedClass:,linkedType:,index:),(name:"rules",type:12,offset:1,mandatory:false,notNull:false,min:,max:,linkedClass:,linkedType:17,index:)]'

    result = odb_loads(source)
    expected = {'data': {'defaultClusterId': 3, 'properties': [{'index': None, 'linkedClass': None, 'mandatory': False, 'name': 'mode', 'min': None, 'max': None, 'offset': 0, 'notNull': False, 'linkedType': None, 'type': 17}, {'index': None, 'linkedClass': None, 'mandatory': False, 'name': 'rules', 'min': None, 'max': None, 'offset': 1, 'notNull': False, 'linkedType': 17, 'type': 12}], 'name': 'ORole', 'clusterIds': [3], 'id': 0}, 'class': None}

    eq_(result, expected)


def test_odb_loads3():
    source = 'ORole@name:"reader",inheritedRole:,mode:0,rules:{"database":2,"database.cluster.internal":2,"database.cluster.orole":2,"database.cluster.ouser":2,"database.class.*":2,"database.cluster.*":2,"database.query":2,"database.command":2,"database.hook.record":2}'

    result = odb_loads(source)
    expected = {'data': {'rules': {'database': 2, 'database.cluster.internal': 2, 'database.class.*': 2, 'database.cluster.ouser': 2, 'database.command': 2, 'database.hook.record': 2, 'database.cluster.orole': 2, 'database.query': 2, 'database.cluster.*': 2}, 'inheritedRole': None, 'name': 'reader', 'mode': 0}, 'class': 'ORole'}

    eq_(result, expected)



from orientdb.coder import escape, unescape
def escape_test():

    real = escape('asdf"g\\h')
    expected = 'asdf\\"g\\\\h'

    eq_(real, expected)



def unescape_test():
    real = unescape('asdf\\"g\\\\h')
    expected = 'asdf"g\\h'

    eq_(real, expected)

