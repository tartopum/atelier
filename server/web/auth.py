from flask_httpauth import HTTPBasicAuth

from ..config import config


auth = HTTPBasicAuth()


@auth.get_password
def get_pw(username):
    user, pwd = config["server"]["http_credentials"]
    if user != username:
        return None
    return pwd
