from Jumpscale import j
from unittest import TestCase


def main(self):
    """
    to run:
    kosmos 'j.data.bcdb.test(name="vfs")'

    """

    SCHEMA = """
    @url = threefoldtoken.wallet.test
    name* = "wallet"
    addr = ""                   # Address
    ipaddr = (ipaddr)           # IP Address
    email = "" (S)              # Email address
    username = "" (S)           # User name
    
    """
    # md5 = "cbf134f55d0c7149ef188cf8a52db0eb"
    # sid = "7"

    bcdb = j.data.bcdb.get("test")
    bcdb.reset()
    m = bcdb.model_get_from_schema(SCHEMA)
    test_case = TestCase()
    for i in range(10):
        o = m.new()
        assert o._model.schema.url == "threefoldtoken.wallet.test"
        o.addr = "something:%s" % i
        o.email = "myemail"
        o.name = "myuser_%s" % i
        o.save()

    # we now have some data
    assert len(m.find()) == 10
    r = m.get_by_name("myuser_8")
    assert r[0].addr == "something:8"

    vfs = j.data.bcdb._get_vfs()
    r = vfs.get("/")
    bcdb_names = [i for i in r.list()]
    assert "test" in bcdb_names
    r = vfs.get("/test")
    indentifiers = [i for i in r.list()]
    print(indentifiers)
    assert "data" in indentifiers

    r = vfs.get("/test/data")
    namespaces = [i for i in r.list()]
    print("TODO@@@@@@@@@@@@@@@@@@@namespaces")
    # assert 1 in namespaces

    assert "system" in bcdb_names
    r = vfs.get("/system/data")
    namespaces = [i for i in r.list()]
    print(namespaces)
    assert "1" in namespaces
    self._log_info("TEST ROOT DIR DONE")

    with test_case.assertRaises(Exception):
        r = vfs.get("test/schema/md5")
        r = vfs.get("schemas/1")
        r = vfs.get("test/schema/sid/5/78")
        r = vfs.get("test/data/md5")
        r = vfs.get("test/data/2/md6")

    r = vfs.get("test/data/1")
    identifier_folders = [i for i in r.list()]
    assert (
        len(identifier_folders) == 3
        and "sid" in identifier_folders
        and "url" in identifier_folders
        and "hash" in identifier_folders
    )
    r = vfs.get("data/1/url")  # current bcdb is test do to last test
    urls = [i for i in r.list()]
    print(urls)
    assert (
        len(urls) == 9
        and "jumpscale.bcdb.circle.2" in urls
        and "jumpscale.bcdb.acl.circle.2" in urls
        and "threefoldtoken.wallet.test" in urls
    )
    r = vfs.get("/data/1/url/threefoldtoken.wallet.test/")

    objs = [i for i in r.list()]
    print(objs)
    assert len(objs) == 10
    for o in objs:
        obj = j.data.serializers.json.loads(o)
        if obj["addr"] == "something:5":
            assert obj["name"] == "myuser_5"

    r = vfs.get("/data/1/hash/cbf134f55d0c7149ef188cf8a52db0eb/8")

    obj = j.data.serializers.json.loads(r.get())

    assert obj["id"] == 8
    assert str(obj["addr"]).startswith("something:")
    assert str(obj["name"]).startswith("myuser_")
    self._log_info("TEST GET DATA DONE")

    # schema path
    r = vfs.get("schemas/sid/")
    r2 = vfs.get("schemas/hash/")
    r3 = vfs.get("schemas/url/")
    schemas = [i for i in r.list()]
    schemas2 = [i for i in r2.list()]
    schemas3 = [i for i in r3.list()]
    print(schemas)
    print(schemas2)
    print(schemas3)
    assert len(schemas) == len(schemas2) == 7
    assert len(schemas3) == 9  # multiple url link to the same schema id ?
    r = vfs.get("schemas/url/threefoldtoken.wallet.test")
    schema = r.get()
    obj = j.data.serializers.json.loads(schema)
    assert str(obj["url"]) == "threefoldtoken.wallet.test"
    assert str(obj["name"]) == "string"
    self._log_info("TEST GET SCHEMA DONE")

    r = vfs.get("data/1/url/threefoldtoken.wallet.test/1")
    obj = r.get()
    r.delete()
    with test_case.assertRaises(Exception):
        r_deleted = vfs.get("data/1/url/threefoldtoken.wallet.test/1")
    r2 = vfs.get("data/1/url/threefoldtoken.wallet.test/2")
    obj2raw = r2.get()

    obj2 = j.data.serializers.json.loads(obj2raw)
    assert obj2["name"] == "myuser_1"
    assert obj2["id"] == 2

    with test_case.assertRaises(Exception):
        obj = r_deleted.get()  # can't get deleted data
    self._log_info("TEST DELETE DATA DONE")

    SCHEMAS = """
    @url = ben.pc.test
    description* = "top_pc"
    cpu = "6ghz" (S)            # power
    ram =  (LI)                   
    enable = true (B)  
    @url = ben.pc.test.2
    description* = "super_top_pc"
    cpu = "12ghz" (S)            # power
    ram =  (LI)                   
    enable = false (B)            
    """
    res = vfs.add_schemas(SCHEMAS)
    s = vfs.get(res[0])
    obj = j.data.serializers.json.loads(s.get())
    assert obj["url"] == "ben.pc.test"
    sch_dir = vfs.get("data/1/url")
    assert "ben.pc.test.2" in [i for i in sch_dir.list()]
    self._log_info("TEST SET SCHEMAS DONE")

    def get_obj(i):
        model_obj = m.new()
        model_obj.email = "ben%s@threefoldtech.com" % i
        model_obj.username = "incredible_username%s" % i
        return model_obj

    model_obj = get_obj(1)
    # j.shell()
    # vx = vfs.set(model_obj)
    # model.set_dynamic(model_obj)

    self._log_info("TEST SET DATA DONE")

    self._log_info("TEST SET SCHEMA DONE")
    vfs.delete("/")
    self._log_info("TEST DONE")
    return "OK"