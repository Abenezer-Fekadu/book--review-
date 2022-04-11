from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash


class User():
    def __init__(self, username, email, password):
        self.username = username.title()
        self.email = email.title()
        self.pwdhash = password.title()

    def set_password(self, password):
        self.pwdhash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(str(self.pwdhash), password)
