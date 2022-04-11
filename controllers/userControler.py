from db.sql_run import run_sql
from werkzeug.security import check_password_hash, generate_password_hash
from users import User


def addNewUser(user):
    user.set_password(user.pwdhash)
    sql = "INSERT INTO users (username, email, pwdhash) VALUES(%(username)s, %(email)s, %(password)s)"
    values = {'username': user.username,
              'email': user.email, 'password': user.pwdhash}
    result = run_sql(sql, values)
    print(result)


def getUser(email, password):
    user = None
    sql = "SELECT * FROM users WHERE lower(email) = lower(%(email)s)"
    values = {'email': email}
    result = run_sql(sql, values)
    if result:
        if check_password_hash(result[0]['pwdhash'], password):
            user = User(result[0]['username'], result[0]
                        ['email'], result[0]['pwdhash'])
    return user


def checkUser(email):
    user = None
    sql = "SELECT * FROM users WHERE lower(email) = lower(%(email)s)"
    values = {'email': email}
    result = run_sql(sql, values)
    if result:
        user = User(result[0]['username'],
                    result[0]['email'], result[0]['pwdhash'])
    return user


def checkUsername(username):
    user = None
    sql = "SELECT * FROM users WHERE username = %(username)s"
    values = {'username': username}
    result = run_sql(sql, values)
    if result:
        user = User(result[0]['username'],
                    result[0]['email'], result[0]['pwdhash'])
    return user
