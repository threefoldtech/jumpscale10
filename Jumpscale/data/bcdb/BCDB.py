# from importlib import import_module

import gevent
from Jumpscale.clients.stor_zdb.ZDBClientBase import ZDBClientBase
from Jumpscale.clients.stor_rdb.RDBClient import RDBClient
from gevent import queue
from .BCDBModel import BCDBModel
from .BCDBMeta import BCDBMeta
from .BCDBDecorator import *
from .connectors.redis.RedisServer import RedisServer
from .BCDBIndexMeta import BCDBIndexMeta
from Jumpscale import j
import sys
from .DBSQLite import DBSQLite

JSBASE = j.application.JSBaseClass


class BCDB(j.application.JSBaseClass):
    def __init__(self, name=None, storclient=None, reset=False):
        """
        :param name: name for the BCDB
        :param storclient: if storclient == None then will use sqlite db
        """
        JSBASE.__init__(self)

        self._redis_index = j.clients.redis.core

        if name is None:
            raise RuntimeError("name needs to be specified")

        if storclient is not None:
            if not isinstance(storclient, ZDBClientBase) and not isinstance(storclient, RDBClient):
                raise RuntimeError("storclient needs to be type: clients.zdb.ZDBClientBase or clients.rdb")

        self.name = name
        self._sqlclient = None
        self.dataprocessor_greenlet = None

        self._data_dir = j.sal.fs.joinPaths(j.dirs.VARDIR, "bcdb", self.name)
        self.storclient = storclient

        self.meta = BCDBMeta(self, reset=True)

        self._init_(reset=reset, stop=False)

        self._need_to_reset = reset
        assert self.name
        j.data.bcdb._bcdb_instances[self.name] = self

        if not j.data.types.string.check(self.name):
            raise RuntimeError("name needs to be string")

        j.data.nacl.default

    def export(self, path=None, encrypt=True):
        if not path:
            raise RuntimeError("export no path")

        for o in list(self.meta._data.schemas):
            m = self.model_get_from_schema(o.text)
            dpath = "%s/%s__%s" % (path, m.schema.url, m.schema._md5)
            j.sal.fs.createDir(dpath)
            dpath_file = "%s/meta.schema" % (dpath)
            j.sal.fs.writeFile(dpath_file, m.schema.text)
            for obj in list(m.iterate()):
                if obj._model.schema.url == o.url:
                    json = obj._json
                    if encrypt:
                        ext = ".encr"
                        json = j.data.nacl.default.encryptSymmetric(json)
                    else:
                        ext = ""
                    if "name" in obj._ddict:
                        dpath_file = "%s/%s__%s.json%s" % (dpath, obj.name, obj.id, ext)
                    else:
                        dpath_file = "%s/%s.json%s" % (dpath, obj.id, ext)
                    j.sal.fs.writeFile(dpath_file, json)

    def import_(self, path=None, reset=True):
        if not path:
            raise RuntimeError("export no path")
        if reset:
            self.reset()
            if self.storclient:
                assert self.storclient.list() == [0]
        self._log_info("Load bcdb:%s from %s" % (self.name, path))
        assert j.sal.fs.exists(path)

        data = {}
        models = {}
        max = 0
        # first load all schemas
        for schema_id in j.sal.fs.listDirsInDir(path, False, dirNameOnly=True):
            url, md5 = schema_id.split("__")
            schema_path = "%s/%s" % (path, schema_id)
            schema_text = j.sal.fs.readFile("%s/meta.schema" % schema_path)
            schema = j.data.schema.add_from_text(schema_text)[0]
            model = self.model_get_from_schema(schema)
            models[md5] = model
        # now load the data
        for schema_id in j.sal.fs.listDirsInDir(path, False, dirNameOnly=True):
            schema_path = "%s/%s" % (path, schema_id)
            url, md5 = schema_id.split("__")
            print("MD5: %s" % md5)
            model = models[md5]
            assert model.schema._md5 == md5
            for item in j.sal.fs.listFilesInDir(schema_path, False):
                if j.sal.fs.getFileExtension(item) == "encr":
                    self._log("encr:%s" % item)
                    encr = True
                elif j.sal.fs.getFileExtension(item) == "json":
                    self._log("json:%s" % item)
                    encr = False
                else:
                    self._log("skip:%s" % item)
                    continue
                base = j.sal.fs.getBaseName(item)
                if base.find("__") != -1:
                    obj_id = int(base.split("__")[1].split(".")[0])
                else:
                    obj_id = int(base.split(".")[0])
                if obj_id in data:
                    raise RuntimeError("id's need to be unique, cannot import")
                json = j.sal.fs.readFile(item, binary=encr)
                if encr:
                    json = j.data.nacl.default.decryptSymmetric(json)
                data[obj_id] = (md5, json)
                if obj_id > max:
                    max = obj_id

        if self.storclient:
            assert self.storclient.nsinfo["mode"] == "sequential"
            assert self.storclient.nsinfo["entries"] == 1
            lastid = 1

        # have to import it in the exact same order
        for i in range(1, max + 1):
            self._log("import: %s" % json)
            if self.storclient:
                if self.storclient.get(key=i - 1) is None:
                    obj = model.new()
                    obj.id = None
                    obj.save()
            if i in data:
                md5, json = data[i]
                model = models[md5]
                if self.storclient:
                    if self.storclient.get(key=i) is None:
                        # does not exist yet
                        try:
                            obj = model.new(data=json)
                        except:
                            raise RuntimeError("can't get a new model based on json data:%s" % json)
                        if self.storclient:
                            obj.id = None
                    else:
                        obj = model.get(obj.id)
                        # means it exists, need to update, need to check if data is different only save if y
                else:
                    obj = model.get(i, die=False)
                    if not obj:
                        obj = model.new(data=json)
                obj.save()
                assert obj.id == i

    @property
    def sqlclient(self):
        if self._sqlclient is None:
            self._sqlclient = DBSQLite(self)
        return self._sqlclient

    def _init_(self, stop=True, reset=False):

        if stop:
            self.stop()

        self._sqlclient = None

        self.dataprocessor_start()

        self.acl = None
        self.user = None
        self.circle = None

        self._index_schema_class_cache = {}  # cache for the index classes

        if reset:
            self._reset()

        if reset:
            j.clients.credis_core.delete(self.meta._redis_key_inited)  # because now we need to reload all

        j.sal.fs.createDir(self._data_dir)

        # needed for async processing
        self.results = {}
        self.results_id = 0

        # need to do this to make sure we load the classes from scratch
        for item in ["ACL", "USER", "GROUP"]:
            key = "Jumpscale.data.bcdb.models_system.%s" % item
            if key in sys.modules:
                sys.modules.pop(key)

        # check if we need to rebuild the BCDB indexes
        try:
            res = j.clients.credis_core.get(self.meta._redis_key_inited)
        except j.clients.credis_core._ConnectionError:
            j.clients.credis_core._init()
            res = j.clients.credis_core.get(self.meta._redis_key_inited)
        except Exception as e:
            raise e

        if not res:
            # means there is no index yet in the redis, need to rebuild all
            self.index_rebuild()

        from .models_system.ACL import ACL
        from .models_system.USER import USER
        from .models_system.CIRCLE import CIRCLE
        from .models_system.NAMESPACE import NAMESPACE

        self.acl = self.model_add(ACL(bcdb=self))
        self.user = self.model_add(USER(bcdb=self))
        self.circle = self.model_add(CIRCLE(bcdb=self))
        self.NAMESPACE = self.model_add(NAMESPACE(bcdb=self))

        j.clients.credis_core.set(self.meta._redis_key_inited, b"1")

        self._log_info("BCDB INIT DONE:%s" % self.name)

    def redis_server_start(self, port=6380, secret="123456"):

        self.redis_server = RedisServer(bcdb=self, port=port, secret=secret, addr="0.0.0.0")
        self.redis_server.init()
        self.redis_server.start()

    def _data_process(self):
        # needs gevent loop to process incoming data
        self._log_info("DATAPROCESSOR STARTS")
        while True:
            method, args, kwargs, event, returnid = self.queue.get()
            if args == ["STOP"]:
                break
            else:
                res = method(*args, **kwargs)
                if returnid:
                    self.results[returnid] = res
                event.set()
        self.dataprocessor_greenlet = None
        event.set()
        self._log_warning("DATAPROCESSOR STOPS")

    def dataprocessor_start(self):
        """
        will start a gevent loop and process the data in a greenlet

        this allows us to make sure there will be no race conditions when gevent used or when subprocess
        main issue is the way how we populate the sqlite db (if there is any)

        :return:
        """
        if self.dataprocessor_greenlet is None:
            self.queue = gevent.queue.Queue()
            self.dataprocessor_greenlet = gevent.spawn(self._data_process)
            self.dataprocessor_state = "RUNNING"

    def reset(self):
        """
        resets data & index
        :return:
        """
        self._init_(stop=True, reset=True)

    def destroy(self):
        self.reset()
        j.data.bcdb._config.pop(self.name)
        if self.name in j.data.bcdb._bcdb_instances:
            j.data.bcdb._bcdb_instances.pop(self.name)
        j.data.bcdb._config_write()
        for key in j.core.db.keys("bcdb:%s:*" % self.name):
            j.core.db.delete(key)

    def _reset(self):

        if self.storclient:
            self.storclient.flush(meta=self.meta)  # new flush command

        self._redis_reset()
        self.meta.reset()

        if self._sqlclient is not None:
            self.sqlclient.close()
            self._sqlclient = None

        j.sal.fs.remove(self._data_dir)

    def _redis_reset(self):
        for key in self._redis_index.keys("bcdb:%s*" % self.name):
            self._redis_index.delete(key)

    def stop(self):
        self._log_info("STOP BCDB")
        if self.dataprocessor_greenlet is not None:
            self.dataprocessor_greenlet.kill()
        self.dataprocessor_greenlet = None

    def index_rebuild(self):
        self._log_warning("REBUILD INDEX")
        self.meta.reset()
        for m in self.models:
            m.index_rebuild()

    @property
    def models(self):

        for key, model in self.meta._sid_to_model.items():
            yield model

    def model_get_from_sid(self, sid, namespaceid=1):
        md5 = None
        if sid in self.meta._sid_to_model:
            return self.meta._sid_to_model[sid]
        else:
            raise RuntimeError("did not find model with sid:'%s' in mem." % sid)

    def model_get_from_url(self, url, namespaceid=1):
        """
        will return the latest model found based on url
        :param url:
        :return:
        """
        s = j.data.schema.get_from_url_latest(url=url)
        return self.model_get_from_schema(s)

    def model_add(self, model):
        """

        :param model: is the model object  : inherits of self.MODEL_CLASS
        :return:
        """
        if not isinstance(model, j.data.bcdb._BCDBModelClass):
            raise RuntimeError("model needs to be of type:%s" % self._BCDBModelClass)
        assert model.sid
        self._schema_property_add_if_needed(model.schema)
        self._schema_add(model.schema)  # do not forget to add the schema

        self.meta._sid_to_model[model.sid] = model

        s = model.schema
        assert self.meta._schema_md5_to_sid[s._md5]
        assert self.meta._schema_md5_to_sid[s._md5] == model.sid

        return model

    def _schema_add(self, schema):
        sid = self.meta._schema_set(schema)  # make sure we remember schema
        return sid

    def _schema_property_add_if_needed(self, schema):
        """
        recursive walks over schema properties (multiple levels)
        if a sub property is a complex type by itself, then we need to make sure we remember the schema's also in BCDB
        :param schema:
        :return:
        """

        for prop in schema.properties:
            if prop.jumpscaletype.NAME == "list" and isinstance(prop.jumpscaletype.SUBTYPE, j.data.types._jsxobject):
                # now we know that there is a subtype, we need to store it in the bcdb as well
                s = prop.jumpscaletype.SUBTYPE._schema
                s = self._schema_add(s)
                # now see if more subtypes
                self._schema_property_add_if_needed(s)
            elif prop.jumpscaletype.NAME == "jsxobject":
                s = prop.jumpscaletype._schema
                s = self._schema_add(s)
                # now see if more subtypes
                self._schema_property_add_if_needed(s)

    def model_get_from_schema(self, schema, sid=None):
        """
        :param schema: is schema as text or as schema obj
        :param reload: will reload template
        :param overwrite: will overwrite the resulting file even if it already exists
        :param namespaceid is the namespace id
        :return:
        """
        if j.data.types.string.check(schema):
            schema_text = schema
            schema = j.data.schema.get_from_text(schema_text)
            self._log_debug("model get from schema:%s, original was text." % schema.url)
        else:
            self._log_debug("model get from schema:%s" % schema.url)
            if not isinstance(schema, j.data.schema.SCHEMA_CLASS):
                raise RuntimeError("schema needs to be of type: j.data.schema.SCHEMA_CLASS")
            schema_text = schema.text

        if not sid:
            if schema._md5 in self.meta._schema_md5_to_sid:
                sid = self.meta._schema_md5_to_sid[schema._md5]
                # means we already know the schema
            else:
                sid = self._schema_add(schema)  # this will make sure the schema is registered on the metadata level

        if sid in self.meta._sid_to_model:
            return self.meta._sid_to_model[sid]

        # model not known yet need to create
        self._log_info("load model:%s" % schema.url)
        model = BCDBModel(bcdb=self, schema=schema, sid=sid)
        return self.model_add(model)

    def _BCDBModelIndexClass_generate(self, schema):
        """

        :param schema: is schema object j.data.schema... or text
        :return: class of the model which is used for indexing

        """
        self._log_debug("generate schema:%s" % schema.url)

        if j.data.types.string.check(schema):
            schema = j.data.schema.get_from_text(schema)

        elif not isinstance(schema, j.data.schema.SCHEMA_CLASS):
            raise RuntimeError("schema needs to be of type: j.data.schema.SCHEMA_CLASS")

        if schema.key not in self._index_schema_class_cache:

            # model with info to generate
            imodel = BCDBIndexMeta(schema=schema)
            imodel.include_schema = True
            tpath = "%s/templates/BCDBModelIndexClass.py" % j.data.bcdb._path
            myclass = j.tools.jinja2.code_python_render(
                path=tpath, objForHash=schema._md5, reload=True, schema=schema, bcdb=self, index=imodel
            )

            self._index_schema_class_cache[schema.key] = myclass

        return self._index_schema_class_cache[schema.key]

    def model_get_from_file(self, path):
        """
        add model to BCDB
        is path to python file which represents the model

        """
        self._log_debug("model get from file:%s" % path)
        obj_key = j.sal.fs.getBaseName(path)[:-3]
        cl = j.tools.codeloader.load(obj_key=obj_key, path=path, reload=False)
        model = cl()
        return self.model_add(model)

    def models_add(self, path, overwrite=True):
        """
        will walk over directory and each class needs to be a model
        when overwrite used it will overwrite the generated models (careful)
        :param path:
        :return: None
        """
        self._log_debug("models_add:%s" % path)

        if not j.sal.fs.isDir(path):
            raise RuntimeError("path: %s needs to be dir, to load models from" % path)

        pyfiles_base = []
        for fpath in j.sal.fs.listFilesInDir(path, recursive=True, filter="*.py", followSymlinks=True):
            pyfile_base = j.tools.codeloader._basename(fpath)
            if pyfile_base.find("_index") == -1:
                pyfiles_base.append(pyfile_base)

        tocheck = j.sal.fs.listFilesInDir(path, recursive=True, filter="*.toml", followSymlinks=True)
        # Try to load all schemas from directory
        # if one schema depends to another it will fail to load if the other one is not loaded yet
        # that's why we keep the errored schemas and put it to the end of the queue so it waits until every thing is
        # loaded and try again we will do that for 3 times as max for each schema
        errored = {}
        while tocheck != []:
            schemapath = tocheck.pop()
            bname = j.sal.fs.getBaseName(schemapath)[:-5]
            if bname.startswith("_"):
                continue
            dest = "%s/%s.py" % (path, bname)
            schema_text = j.sal.fs.readFile(schemapath)
            try:
                schema = j.data.schema.get_from_text(schema_text)
                self._schema_add(schema)
                model = self.model_get_from_schema(schema=schema)
                toml_path = "%s.toml" % (schema.key)
                if j.sal.fs.getBaseName(schemapath) != toml_path:
                    toml_path = "%s/%s.toml" % (j.sal.fs.getDirName(schemapath), schema.key)
                    j.sal.fs.renameFile(schemapath, toml_path)
                    schemapath = toml_path
            except:
                error_count = errored.get(schemapath, 0)
                if error_count > 3:
                    raise e
                tocheck.insert(0, schemapath)
                continue

        for pyfile_base in pyfiles_base:
            if pyfile_base.startswith("_"):
                continue
            path2 = "%s/%s.py" % (path, pyfile_base)
            self.model_get_from_file(path2)

    def _unserialize(self, id, data, return_as_capnp=False, model=None):
        """
        unserialzes data coming from database
        :param id:
        :param data:
        :param return_as_capnp:
        :param model:
        :return:
        """
        res = j.data.serializers.msgpack.loads(data)

        if len(res) == 3:
            raise RuntimeError()
        elif len(res) == 4:
            nid, schema_id, acl_id, bdata_encrypted = res
            model = self.model_get_from_sid(schema_id)
        else:
            raise RuntimeError("not supported format")

        bdata = j.data.nacl.default.decryptSymmetric(bdata_encrypted)

        if return_as_capnp:
            return bdata
        else:
            try:
                obj = model.schema.new(serializeddata=bdata, model=model)
            except Exception as e:
                msg = "can't get a model from data:%s\n%s" % (bdata, e)
                print(msg)
                raise RuntimeError(msg)
            obj.nid = nid
            obj.id = id
            obj.acl_id = acl_id
            obj._model = model
            if model.readonly:
                obj.readonly = True  # means we fetched from DB, we need to make sure it cannot be changed
            return obj

    def obj_get(self, id):
        data = self.storclient.get(id)
        if data is None:
            return None
        return self._unserialize(id, data)

    def iterate(self, key_start=None, reverse=False, keyonly=False):
        """
        walk over all the namespace and yield each object in the database

        :param key_start: if specified start to walk from that key instead of the first one, defaults to None
        :param key_start: str, optional
        :param reverse: decide how to walk the namespace
                if False, walk from older to newer keys
                if True walk from newer to older keys
                defaults to False
        :param reverse: bool, optional
        :param keyonly: [description], defaults to False
        :param keyonly: bool, optional
        :raises e: [description]
        """
        if self.storclient:
            db = self.storclient
            for key, data in db.iterate(key_start=key_start, reverse=reverse, keyonly=keyonly):
                if self.storclient.type.lower() == "zdb" and key == 0:  # skip first metadata entry
                    continue
                if keyonly:
                    yield key
                elif data:
                    obj = self._unserialize(key, data)
                else:
                    obj = ""

                yield obj
        else:
            for key, data in self.sqlclient.iterate():
                if key == 0:  # skip first metadata entry
                    continue
                obj = self._unserialize(key, data)
                yield obj

    def get_all(self):
        return [obj for obj in self.iterate()]

    def __str__(self):
        out = "bcdb:%s\n" % self.name
        return out

    __repr__ = __str__
