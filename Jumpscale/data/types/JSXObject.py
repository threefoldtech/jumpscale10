from Jumpscale import j
from Jumpscale.data.types.TypeBaseClasses import TypeBaseObjFactory


class JSDataObjectFactory(TypeBaseObjFactory):
    '''
    jumpscale data object as result of using j.data.schemas.
    '''
    NAME = 'jsobject,o,obj'
    CUSTOM = True

    def __init__(self):
        self.BASETYPE = 'bin'
        self.SUBTYPE = None

    def __init__(self,default = None):
        """

        :param schema_url: is the url to a jumpscale schema
        """
        if not default:
            raise j.exceptions.Input("Cannot init JSDataObjectFactory without url")
        self._schema_url = default
        self._schema_ = None

    @property
    def _schema(self):
        """
        JSX schema for the child
        :return:
        """
        if self._schema_ is None:
            self._schema_ = j.data.schemas.get(url=self._schema_url)
        return self._schema_

    def python_code_get(self, value):
        raise NotImplemented()

    def fromString(self, s):
        """
        will use json
        """
        return self.clean(val)

    def toString(self,val):
        """
        will use json
        :param v:
        :return:
        """
        val = self.clean(val)
        return val._json

    def check(self, value):
        return isinstance(value,j.data.schemas._DataObjBase)

    def default_get(self):
        return self._schema.new()

    def clean(self, value,model=None):
        """

        :param value: is the object which needs to be converted to a data object
        :param model: when model specified (BCDB model) can be stored in BCDB
        :return:
        """
        if isinstance(value,j.data.schemas._DataObjBase):
            return value
        if isinstance(value,bytes):
            return self._schema.get(data=None, capnpbin=value, model=model)
        else:
            return self._schema.get(data=value, capnpbin=None, model=model)

    def toHR(self, v):
        v=self.clean(v)
        return str(v)

    def capnp_schema_get(self, name, nr):
        raise NotImplemented()

    def toml_string_get(self, value, key):
        raise NotImplemented()


class JSConfigObject(TypeBaseObjFactory):
    '''
    jumpscale object which inherits from j.application.JSBaseConfigClass
    '''
    NAME =  'jsconfigobject,configobj'

    def __init__(self):

        self.BASETYPE = 'capnpbin'
        self.SUBTYPE = None

    def check(self, value):
        return isinstance(value, j.application.JSBaseConfigClass)

    def clean(self,value):
        if isinstance(value, j.application.JSBaseConfigClass):
            return value
        raise NotImplemented("TODO")