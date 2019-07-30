import textwrap

from Jumpscale import j

builder_method = j.builders.system.builder_method

# /tmp is the default directory for postgres unix socket
SIMPLE_CFG = """
[options]
admin_passwd = rooter
db_host = localhost
db_user = root"""


class BuilderOdoo(j.builders.system._BaseClass):
    NAME = "odoo"

    def _init(self, **kwargs):
        self.VERSION = "12.0"
        self.APP_DIR = self._replace("{DIR_BASE}/apps/odoo")

    @builder_method()
    def configure(self):
        pass

    @builder_method()
    def install(self):
        """
        kosmos 'j.builders.apps.odoo.install()'
        kosmos 'j.builders.apps.odoo.start()'
        install odoo
        """
        j.builders.db.postgres.install()
        j.builders.runtimes.nodejs.install()

        self.tools.dir_ensure(self.APP_DIR)

        j.builders.system.package.install(
            "sudo libxml2-dev libxslt1-dev libsasl2-dev python3-dev libldap2-dev libssl-dev"
        )

        self._execute(
            """
        cd {APP_DIR}

        if [ ! -d odoo/.git ]; then
            git clone https://github.com/odoo/odoo.git -b {VERSION} --depth=1
        fi

        cd odoo
        # sudo -H -u odoouser python3 -m pip install --user -r requirements.txt
        python3 setup.py  install
        chmod +x odoo-bin
        """
        )

        j.builders.runtimes.nodejs.npm_install("rtlcss")

        print("INSTALLED OK, PLEASE GO TO http://localhost:8069")
        # print("INSTALLED OK, PLEASE GO TO http://localhost:8069/web/database/selector")

    def start(self):
        """
        kosmos 'j.builders.apps.odoo.start()'
        :return:
        """
        j.builders.db.postgres.start()
        cl = j.clients.postgres.db_client_get()
        self._write("{DIR_CFG}/odoo.conf", SIMPLE_CFG)
        j.builders.system._BaseClass.start(self)
        print("INSTALLED OK, PLEASE GO TO http://localhost:8069    masterpasswd:rooter")

    def stop(self):
        j.builders.db.postgres.stop()
        j.builders.system._BaseClass.stop(self)

    @property
    def startup_cmds(self):
        """
        j.builders.apps.odoo.startup_cmds
        :return:
        """

        # odoo_start = self._replace(
        #     "sudo -H -u odoouser python3 /sandbox/apps/odoo/odoo/odoo-bin -c {DIR_CFG}/odoo.conf"
        # )
        odoo_start = self._replace("python3 /sandbox/apps/odoo/odoo/odoo-bin -c {DIR_CFG}/odoo.conf")
        odoo_cmd = j.servers.startupcmd.get("odoo")
        odoo_cmd.cmd_start = odoo_start
        odoo_cmd.process_strings = "/sandbox/apps/odoo/odoo/odoo-bin -c"
        odoo_cmd.path = "/sandbox/bin"
        odoo_cmd.ports = [8069]
        return [odoo_cmd]
