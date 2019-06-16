from pyblake2 import blake2b
from Jumpscale import j


import struct
from .BCDBDecorator import *

JSBASE = j.application.JSBaseClass
INT_BIN_EMPTY = b"\xff\xff\xff\xff"  # is the empty value for in our key containers

from .BCDBModelIndex import BCDBModelIndex


class BCDBModel(j.application.JSBaseClass):
    def __init__(self, bcdb, schema=None, reset=False):
        """

        delivers interface how to deal with data in 1 schema

        for query example see http://docs.peewee-orm.com/en/latest/peewee/query_examples.html

        e.g.
        ```
        query = self.index.name.select().where(index.cost > 0)
        for item in self.select(query):
            print(item.name)
        ```
        """

        JSBASE.__init__(self)

        bcdb, schema, reset = self._init_load(bcdb, schema, reset)

        assert bcdb
        assert schema
        assert schema.sid > 0

        self.schema = schema
        self.bcdb = bcdb
        self.zdbclient = bcdb.zdbclient
        self.readonly = False
        self.autosave = False  # if set it will make sure data is automatically set from object

        if self.zdbclient and self.zdbclient.type == "ZDB":
            # is unique id for a bcdbmodel (unique per zdbclient !)
            self.key = "%s_%s" % (self.zdbclient.nsname, self.schema.url)
        else:
            self.key = self.schema.url
        self.key = self.key.replace(".", "_")

        self._data_dir = j.sal.fs.joinPaths(self.bcdb._data_dir, self.key)
        j.sal.fs.createDir(self._data_dir)

        self._kosmosinstance = None

        indexklass = bcdb._BCDBModelIndexClass_generate(schema)
        self.index = indexklass(self, reset=reset)

        # self.cache_expiration = 3600

        self._triggers = []

        if reset:
            self.reset()

    def _init_load(self, bcdb, schema, reset):
        return bcdb, schema, reset

    def trigger_add(self, method):
        """
        see docs/baseclasses/data_mgmt_on_obj.md

        triggers are called with obj,action,propertyname as kwargs

        return obj or None

        :param method:
        :return:
        """
        if method not in self._triggers:
            self._triggers.append(method)

    def triggers_call(self, obj, action=None, propertyname=None):
        """
        will go over all triggers and call them with arguments given
        see docs/baseclasses/data_mgmt_on_obj.md

        """
        model = self
        kosmosinstance = self._kosmosinstance
        for method in self._triggers:
            obj2 = method(model, obj, kosmosinstance=kosmosinstance, action=action, propertyname=propertyname)
            if isinstance(obj2, j.data.schema.DataObjBase):
                # only replace if right one returned, otherwise ignore
                obj = obj2
            else:
                if obj2 is not None:
                    raise RuntimeError("obj return from action needs to be a JSX data obj or None")
        return obj

    # def cache_reset(self):
    #     self.obj_cache = {}

    @queue_method
    def index_ready(self):
        """
        doesn't do much, just makes sure that we wait that queue has been processed upto this point
        :return:
        """
        return True

    def stop(self):
        """
        stops the data processor
        """
        if self.bcdb.dataprocessor_greenlet is None:
            # is already stopped
            return True
        event = Event()
        self.bcdb.queue.put((None, ["STOP"], {}, event, None))

        event.wait(1000.0)  # will wait for processing
        if self.bcdb._sqlclient is not None:
            self.bcdb.sqlclient.close()
            self.bcdb._sqlclient = None

        self._log_info("DATAPROCESSOR & SQLITE STOPPED OK")
        return True

    # def start(self):
    #     if self.dataprocessor_greenlet is None:
    #         self.bcdb.dataprocessor_start()
    #     self.index_ready() #will only return when dataprocessor working

    @queue_method
    def index_rebuild(self, nid=1):
        self.stop()
        self.index.destroy(nid=nid)
        self._log_warning("will rebuild index for:%s" % self)
        for obj in self.iterate(nid=nid):
            self.set(obj, store=False, index=True)

    @queue_method
    def delete(self, obj):
        if not isinstance(obj, j.data.schema.DataObjBase):
            if isinstance(obj, int):
                obj = self.get(obj)
            else:
                raise RuntimeError("specify id or obj")
        assert obj.nid
        if obj.id is not None:
            self.triggers_call(obj=obj, action="delete")
            # if obj.id in self.obj_cache:
            #     self.obj_cache.pop(obj.id)
            if not self.zdbclient:
                self.bcdb.sqlclient.delete(key=obj.id)
            else:
                self.zdbclient.delete(obj.id)
            self.index.delete(obj)

    def check(self, obj):
        if not isinstance(obj, j.data.schema.DataObjBase):
            raise RuntimeError("argument needs to be a jsx data obj")
        assert obj.nid

    @queue_method
    def set_dynamic(self, data, obj_id=None, nid=None):
        """
        if string -> will consider to be json
        if binary -> will consider data for capnp
        if obj -> will check of JSOBJ
        if ddict will put inside JSOBJ
        """
        if j.data.types.string.check(data):
            data = j.data.serializers.json.loads(data)
            if obj_id == None and "id" in data:
                obj_id = data["id"]
            if nid == None:
                if "nid" in data:
                    nid = data["nid"]
                else:
                    raise RuntimeError("need to specify nid")
            obj = self.schema.get(data)
        elif j.data.types.bytes.check(data):
            obj = self.schema.get(data=data)
            if obj_id is None:
                raise RuntimeError("objid cannot be None")
            if not obj.nid:
                if nid:
                    obj.nid = nid
                else:
                    raise RuntimeError("need to specify nid")
        elif isinstance(data, j.data.schema.DataObjBase):
            obj = data
            if obj_id is None and obj.id is not None:
                obj_id = obj.id
            if not obj.nid:
                if nid:
                    obj.nid = nid
                else:
                    raise RuntimeError("need to specify nid")
        elif j.data.types.dict.check(data):
            if obj_id == None and "id" in data:
                obj_id = data["id"]
            if "nid" not in data or not data["nid"]:
                if nid:
                    data["nid"] = nid
                else:
                    raise RuntimeError("need to specify nid")
            obj = self.schema.get(data)
        else:
            raise RuntimeError("Cannot find data type, str,bin,obj or ddict is only supported")
        if not obj.id:
            obj.id = obj_id  # do not forget
        return self.set(obj)

    def get_by_name(self, name, nid=1):
        args = {"name": name}
        return self.find(nid=nid, **args)

    def find(self, nid=1, **args):
        """
        is a the retrieval part of a very fast indexing system
        e.g.
        self.get_from_keys(name="myname",nid=2)
        :return:
        """
        delete_if_not_found = False
        if len(args.keys()) == 0:
            res = []
            for obj in self.iterate(nid=nid):
                if obj is None:
                    raise RuntimeError("iterate should not return None, ever")
                res.append(obj)
            return res

        ids = self.index._key_index_find(nid=nid, **args)

        def check2(obj, args):
            dd = obj._ddict
            for propname, val in args.items():
                if dd[propname] != val:
                    return False
            return True

        res = []
        for id_ in ids:
            res2 = self.get(id_, die=None)
            if res2 is None:
                if delete_if_not_found:
                    for key, val in args.items():
                        self._key_index_delete(key, val, id_, nid=nid)
            else:
                # we now need to check if there was no false positive
                if check2(res2, args):
                    res.append(res2)
                # else:
                #     self._log_warning("index system produced false positive")

        return res

    @queue_method_results
    def set(self, obj, index=True, store=True):
        """
        :param obj
        :return: obj
        """
        self.check(obj)

        if store:

            # later:
            if obj.acl_id is None:
                obj.acl_id = 0

            if obj._acl is not None:
                if obj.acl.id is None:
                    # need to save the acl
                    obj.acl.save()
                else:
                    acl2 = obj._model.bcdb.acl.get(obj.acl.id)
                    if acl2 is None:
                        # means is not in db
                        obj.acl.save()
                    else:
                        if obj.acl.hash != acl2.hash:
                            obj.acl.id = None
                            obj.acl.save()  # means there is acl but not same as in DB, need to save
                            if obj.acl.readonly:
                                obj.acl.readonly = True
                            self._obj_cache_reset()
                obj.acl_id = obj.acl.id

            try:
                bdata = obj._data
            except Exception as e:
                if str(e).find("has no such member") != -1:
                    msg = str(e).split("no such member", 1)[1].split("stack:")
                    raise RuntimeError("Could not serialize capnnp message:%s" % msg)
                else:
                    raise e

            bdata_encrypted = j.data.nacl.default.encryptSymmetric(bdata)

            l = [obj.nid, self.schema.sid, obj.acl_id, bdata_encrypted]
            data = j.data.serializers.msgpack.dumps(l)

            obj = self.triggers_call(obj, action="set_pre")

            # PUT DATA IN DB
            if obj.id is None:
                # means a new one
                if not self.zdbclient:
                    obj.id = self.bcdb.sqlclient.set(key=None, val=data)
                else:
                    obj.id = self.zdbclient.set(data)
                if self.readonly:
                    obj.readonly = True
                self._log_debug("NEW:\n%s" % obj)
            else:
                if not self.zdbclient:
                    self.bcdb.sqlclient.set(key=obj.id, val=data)
                else:
                    try:
                        self.zdbclient.set(data, key=obj.id)
                    except Exception as e:
                        if str(e).find("only update authorized") != -1:
                            raise RuntimeError("cannot update object:%s\n with id:%s, does not exist" % (obj, obj.id))
                        raise

        if index:
            self.index.set(obj)

        obj = self.triggers_call(obj=obj, action="set_post")

        return obj

    def _dict_process_out(self, ddict):
        """
        whenever dict is needed this method will be called before returning
        :param ddict:
        :return:
        """
        return ddict

    def _dict_process_in(self, ddict):
        """
        when data is inserted back into object
        :param ddict:
        :return:
        """
        return ddict

    def new(self, data=None, nid=1):
        if data and isinstance(data, dict):
            data = self._dict_process_in(data)
        elif j.data.types.json.check(str(data)):
            data = j.data.serializers.json.loads(data)
        if data:
            obj = self.schema.get(data=data, model=self)
        else:
            obj = self.schema.new(model=self)
        obj = self._methods_add(obj)
        obj.nid = nid
        obj = self.triggers_call(obj=obj, action="new")
        return obj

    def _methods_add(self, obj):
        return obj

    @queue_method_results
    def get(self, obj_id, return_as_capnp=False, usecache=True, die=True):
        """
        @PARAM id is an int or a key
        @PARAM capnp if true will return data as capnp binary object,
               no hook will be done !
        @RETURN obj    (.index is in obj)
        """

        if obj_id in [None, 0, "0", b"0"]:
            raise RuntimeError("id cannot be None or 0")

        # if self.obj_cache is not None and usecache:
        #     # print("use cache")
        #     if obj_id in self.obj_cache:
        #         epoch, obj = self.obj_cache[obj_id]
        #         if j.data.time.epoch > self._cache_expiration + epoch:
        #             self.obj_cache.pop(obj_id)
        #             # print("dirty cache")
        #         else:
        #             # print("cache hit")
        #             return obj

        if not self.zdbclient:
            data = self.bcdb.sqlclient.get(key=obj_id)
        else:
            data = self.zdbclient.get(obj_id)

        if not data:
            if die:
                raise RuntimeError("could not find obj with id:%s" % obj_id)
            else:
                return None

        obj = self.bcdb._unserialize(obj_id, data, return_as_capnp=return_as_capnp, model=self)
        # self.obj_cache[obj_id] = (j.data.time.epoch, obj)  #FOR NOW NO CACHE, UNSAFE

        obj = self.triggers_call(obj=obj, action="get")

        return obj

    def destroy(self, nid=1):
        self._log_warning("destroy: %s nid:%s" % (self, nid))
        if self.zdbclient:
            for obj_id in self._id_iterator(nid=nid):
                if not self.zdbclient:
                    self.bcdb.sqlclient.delete(key=obj_id)
                else:
                    self.zdbclient.delete(obj_id)
        else:
            j.shell()

        self.index.destroy()
        self.stop()
        j.sal.fs.remove(self._data_dir)

    def iterate(self, nid=1):
        """
        walk over objects which are of type of this model
        """
        for obj_id in self.index._id_iterator(nid=nid):
            self._log_debug("iterate:%s" % obj_id)
            assert obj_id > 0
            o = self.get(obj_id)
            # try:
            #     o = self.get(obj_id)
            # except Exception as e:
            #     if str(e).find("could not find obj") != -1:
            #         self._log_warning("warning: could not find object with id:%s in %s" % (obj_id, self))
            #         continue
            #     else:
            #         raise e
            yield o

    def __str__(self):
        out = "model:%s\n" % self.schema.url
        # out += j.core.text.prefix("    ", self.schema.text)
        return out

    __repr__ = __str__
