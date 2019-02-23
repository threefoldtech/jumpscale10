from Jumpscale import j
from .TypeBaseClasses import *

class EnumerationObj(TypeBaseObjClass):

    @property
    def _string(self):
        if self._data is 0:
            return "UNKNOWN"
        return self._typebase.values[self._data-1]

    @property
    def _python_code(self):
        return "'%s'"%self._string

    @property
    def value(self):
        return self._data

    @value.setter
    def value(self,val):
        obj = self._typebase.clean(val)
        self._data = obj._data


class Enumeration(TypeBaseObjFactory):

    '''
    Generic string type
    stored in capnp as int

    0 is unknown (nill)
    1 is the default

    '''
    NAME =  'enum,enumeration,e'
    CUSTOM = True
    __slots__ = ['values', 'default', "_md5", "_jumpscale_location"]

    def __init__(self, values):


        self.BASETYPE = "int"
        self.NOCHECK = True

        if isinstance(values, str):
            values = values.split(",")
            values = [item.strip().strip("'").strip().strip('"').strip() for item in values]
        if not isinstance(values, list):
            raise RuntimeError("input for enum is comma separated str or list")
        self.values = [item.upper().strip() for item in values]
        self.values.sort()
        self._md5 = j.data.hash.md5_string(str(self))  # so it has the default as well
        j.data.types.enumerations[self._md5] = self
        self._jumpscale_location = "j.data.types.enumerations['%s']" % self._md5

    def capnp_schema_get(self, name, nr):
        return "%s @%s :UInt32;" % (name, nr)


    def toData(self,value):
        try:
            value = int(value)
        except:
            pass
        if isinstance(value, str):
            value_str = value.upper().strip()
            if value_str not in self.values:
                raise RuntimeError("could not find enum:'%s' in '%s'" % (value, self.__repr__()))
            value_id = self.values.index(value_str)+1
        elif isinstance(value, int):
            if value > len(self.values)+1:
                raise RuntimeError("could not find enum id:%s in '%s', too high" % (value, self.__repr__()))
            value_id = value
        else:
            raise RuntimeError("unsupported type for enum, is int or string")
        return value_id

    def get_default(self):
        """
        returns the first one of collection
        :return:
        """
        return self.clean(1)

    def clean(self, value):
        """
        can use int or string,
        will find it and return as string
        """
        if isinstance(value,EnumerationObj):
            return value
        value_id = self.toData(value)
        return EnumerationObj(self,value_id)

    def __str__(self):
        return "ENUM: %s (default:%s)" % (self.__repr__(), self.get_default())

    def __repr__(self):
        return ",".join(self.values)
