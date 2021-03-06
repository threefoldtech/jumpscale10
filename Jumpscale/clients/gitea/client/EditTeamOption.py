# DO NOT EDIT THIS FILE. This file will be overwritten when re-running go-raml.

"""
Auto-generated class for EditTeamOption
"""
from .EnumEditTeamOptionPermission import EnumEditTeamOptionPermission
from six import string_types

from . import client_support


class EditTeamOption(object):
    """
    auto-generated. don't touch.
    """

    @staticmethod
    def create(**kwargs):
        """
        :type description: string_types
        :type name: string_types
        :type permission: EnumEditTeamOptionPermission
        :rtype: EditTeamOption
        """

        return EditTeamOption(**kwargs)

    def __init__(self, json=None, **kwargs):
        pass
        if json is None and not kwargs:
            raise ValueError("No data or kwargs present")

        class_name = "EditTeamOption"
        data = json or kwargs

        # set attributes
        data_types = [string_types]
        self.description = client_support.set_property(
            "description", data, data_types, False, [], False, False, class_name
        )
        data_types = [string_types]
        self.name = client_support.set_property("name", data, data_types, False, [], False, True, class_name)
        data_types = [EnumEditTeamOptionPermission]
        self.permission = client_support.set_property(
            "permission", data, data_types, False, [], False, False, class_name
        )

    def __str__(self):
        return self.as_json(indent=4)

    def as_json(self, indent=0):
        return client_support.to_json(self, indent=indent)

    def as_dict(self):
        return client_support.to_dict(self)
