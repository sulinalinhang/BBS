import uuid
from functools import wraps

from flask import (
    session,
    request,
    abort,
    redirect,
    url_for,
)

from models.user import User
from models.topic import Topic


def current_user():
    uid = session.get('user_id', 0)
    print('uid', uid)
    if uid == 0:
        uid = 1
    u = User.one(id=uid)
    return u


# csrf_tokens = dict()


def csrf_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        token = request.args['token']
        u = current_user()
        # if token in csrf_tokens and csrf_tokens[token] == u.id:
        if token == u.token:
            # csrf_tokens.pop(token)
            return f(*args, **kwargs)
        else:
            abort(401)

    return wrapper


def new_csrf_token():
    u = current_user()
    token = str(uuid.uuid4())
    # csrf_tokens[token] = u.id
    # form = dict(token=token)
    User.update(u.id, token=token)
    return token


def topic_required(f):
    @wraps(f)
    def wrapper():
        u = current_user()
        topic_id = request.args['id']
        t = Topic.one(id=int(topic_id))
        if t.user_id == u.id:
            return f()
        else:
            return redirect(url_for('.index'))
    return wrapper