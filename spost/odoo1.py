import xmlrpc.client

class AuthenticationError(Exception):
    """Raised when authentication with Odoo fails."""
    pass

class OdooClient:
    def __init__(self, url, db, username, password):
        self.url = url
        self.db = db
        self.username = username
        self.password = password
        self.uid = self.authenticate()

    def authentication(self):
        """Authenticates with the Odoo server."""
        common = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/common')
        uid = common.authenticate(self.db, self.username, self.password, {})
        if not uid:
            ##logging.error("Failed to authenticate with provided credentials")
            raise AuthenticationError("Failed to authenticate with Odoo")
            ##logging.info("Authenticated successfully")
        return uid

    def execute_kw(self, model, method, args, kwargs=None):
        """Executes a keyword method on the Odoo server."""
        models = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/object')
        return models.execute_kw(self.db, self.uid, self.password, model, method, args, kwargs or {})

