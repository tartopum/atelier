from flask_httpauth import HTTPBasicAuth

from .. import config


auth = HTTPBasicAuth()


@auth.get_password
def get_pw(username):
    user, pwd = config.get("server", "http_credentials")
    if user != username:
        return None
    return pwd
