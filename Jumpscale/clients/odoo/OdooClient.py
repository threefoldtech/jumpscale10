from Jumpscale import j

try:
    import erppeek

except:
    j.builders.runtimes.python.pip_package_install("ERPpeek")
    import erppeek


JSConfigBase = j.application.JSBaseConfigClass


class OdooClient(JSConfigBase):
    _SCHEMATEXT = """
    @url = jumpscale.odoo.client
    name* = "main" (S)
    host = "127.0.0.1" (S)
    port = "8069"
    username="admin" (S)
    password_ = "admin" (S)
    database = "user" (S)
    """

    def _init(self, **kwargs):
        self._client = None

    @property
    def client(self):
        if not self._client:
            self._client = erppeek.Client(
                "http://{}:{}".format(self.host, self.port),
                db=self.database,
                user=self.username,
                password=self.password_,
            )
        return self._client

    def module_install(self, module_name):
        return self.client.install(module_name)

    def module_remove(self, module_name):
        return self.client.uninstall(module_name)

    def modules_default_install(self):
        modules = [
            # "expenses",
            # "dashboards",
            "contacts",
            # "leaves",
            # "discuss",
            "lunch",
            "maintenance",
            # "slides",
            # "blogs",
            "calendar",
            "fleet",
            # "events",
            "crm",
            "crm_livechat",
            "crm_project",
            "web",
            "portal",
            "website",
            "project",
            "crm",
            # "employees",
            # "inventory",
            # "invoicing",
            # "sales",
            # "nodes",
            # "ecommerce",
            # "purchase",
            # "recruitment",
        ]
        for module in modules:
            self.module_install(module)

    def user_add(self, username, password):
        new_user = self.client.model("res.users").create({"login": username, "name": username})
        new_user.password = password
        return new_user

    def user_delete(self, user, password):
        user_id = self.client.login(user, password)
        user = self.client.model("res.users").get(user_id)
        self.client.login(self.username, self.password_)
        return user.unlink()

    def login(self, user, password):
        return self.client.login(user, password)