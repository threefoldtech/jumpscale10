# Copyright (C) July 2018:  TF TECH NV in Belgium see https://www.threefold.tech/
# In case TF TECH NV ceases to exist (e.g. because of bankruptcy)
#   then Incubaid NV also in Belgium will get the Copyright & Authorship for all changes made since July 2018
#   and the license will automatically become Apache v2 for all code related to Jumpscale & DigitalMe
# This file is part of jumpscale at <https://github.com/threefoldtech>.
# jumpscale is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# jumpscale is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License v3 for more details.
#
# You should have received a copy of the GNU General Public License
# along with jumpscale or jumpscale derived works.  If not, see <http://www.gnu.org/licenses/>.
# LICENSE END


from Jumpscale import j
import random
from uuid import uuid4

from unittest import TestCase


def main(self):
    """
    to run:

    kosmos 'j.data.bcdb.test(name="unique_data")'

    #. Create schema with unique attributes and save it.
    #. Create another object and try to use same name for first one, should fail.
    #. On the second object, try to use same test var for first one, should fail.
    #. On the second object, try to use same new_name for first one, should success.
    #. On the second object, try to use same number for first one, should fail.
    #. Change name of the first object and try to use the first name again, should success.
    #. Change test var of the first object and try to use the first test var again, should success.
    #. Change number of the first object and try to use the first number again, should success.
    #. Delete the second object and create new one.
    #. Set the new object's attributes with the same attributes of the second object, should success. 
    """
    j.core.tools.log("Create schema with unique attributes and save it", level=20)

    scm = """
    @url = test.schema.1
    &name* = "" (S)
    new_name = "" (S)
    &test = "" (S)
    &number = 0 (I)
    """
    test_case = TestCase()

    j.servers.zdb.test_instance_start()
    self.admin_zdb = j.clients.zdb.client_admin_get(port=9901)
    self.admin_zdb.namespace_new("unique", secret="1234")
    self.zdb = j.clients.zdb.client_get(name="unique", port=9901, secret="1234")
    self.bcdb = j.data.bcdb.new("test", storclient=self.zdb, reset=True)
    schema = j.data.schema.get_from_text(scm)
    self.model = self.bcdb.model_get(schema=schema)
    schema_obj = self.model.new()
    name = "s" + str(uuid4()).replace("-", "")[:10]
    new_name = "s" + str(uuid4()).replace("-", "")[:10]
    test = "s" + str(uuid4()).replace("-", "")[:10]
    number = random.randint(1, 99)
    schema_obj.name = name
    schema_obj.new_name = new_name
    schema_obj.test = test
    schema_obj.number = number
    schema_obj.save()

    j.core.tools.log("Create another object and try to use same name for first one, should fail", level=20)
    schema_obj2 = self.model.new()
    schema_obj2.name = name
    schema_obj2.save()
    schema_obj2.name = "s" + str(uuid4()).replace("-", "")[:10]

    j.core.tools.log("On the second object, try to use same test var for first one, should fail", level=20)
    schema_obj2.test = test
    schema_obj2.save()
    schema_obj2.test = "s" + str(uuid4()).replace("-", "")[:10]

    j.core.tools.log("On the second object, try to use same new_name for first one, should success", level=20)
    schema_obj2.new_name = new_name
    schema_obj2.save()

    j.core.tools.log("On the second object, try to use same number for first one, should fail", level=20)
    schema_obj2.number = number
    schema_obj2.save()
    # check that in DB only 1 matches from the past
    r4 = self.model.find(number=number)
    print(r4)
    assert r4[0].id == schema_obj.id

    assert len(r4) == 1  # there should be one in DB and index should return 1
    schema_obj2.save()
    schema_obj2.number = random.randint(100, 199)
    schema_obj.number = random.randint(200, 299)
    schema_obj.save()
    schema_obj2.number = number
    args_search = {"number": schema_obj2.number}
    r = self.model.find(**args_search)
    assert len(r) == 0
    schema_obj2.save()

    j.core.tools.log("Delete the second object and create new one.", level=20)
    name = schema_obj2.name + ""
    test = schema_obj2.test + ""
    number = schema_obj2.number + 0
    args_search = {"number": number}
    r = self.model.find(**args_search)
    assert len(r) == 1
    schema_obj2.delete()
    # lets now check that the index has been cleaned
    args_search = {"number": number}
    r = self.model.find(**args_search)
    assert len(r) == 0
    args_search = {"name": name}
    r = self.model.find(**args_search)
    assert len(r) == 0
    args_search = {"test": test}
    r = schema_obj2._model.find(**args_search)
    assert len(r) == 0

    try:
        schema_obj2.save()
    except:
        assert Exception

    j.core.tools.log(
        "Set the new object's attributes with the same attributes of the second object, should success.", level=20
    )
    schema_obj3 = self.model.new()
    assert schema_obj3.id == None
    schema_obj3.name = name

    schema_obj3.save()

    self.admin_zdb.namespace_delete("unique")
