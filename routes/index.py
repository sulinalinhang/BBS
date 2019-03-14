import os
import uuid

from flask import (
    render_template,
    request,
    redirect,
    session,
    url_for,
    Blueprint,
    abort,
    send_from_directory,
)

from functools import wraps

from models.user import User
from models.reply import Reply

from utils import log

from models.topic import Topic
from routes import *

main = Blueprint('index', __name__)


@main.route("/")
def index():
    u = current_user()
    # token = new_csrf_token()
    return render_template("index.html", user=u)
    # redirect(url_for('my_topic.index'))

@main.route("/register", methods=['POST'])
def register():
    # form = request.args
    form = request.form
    u = User.register(form)
    return redirect(url_for('.index'))


@main.route("/login", methods=['POST'])
def login():
    form = request.form
    u = User.validate_login(form)
    print('login user <{}>'.format(u))
    if u is None:
        # 转到 topic.index 页面
        return redirect(url_for('.index'))
    else:
        # session 中写入 user_id
        session['user_id'] = u.id
        # 设置 cookie 有效期为 永久
        session.permanent = True
        return redirect(url_for('my_topic.index'))


@main.route('/profile')
def profile():
    u = current_user()
    if u is None:
        return redirect(url_for('.index'))
    else:
        return render_template('personal.html', user=u)


@main.route('/user/<string:username>')
def user_detail(username):
    print(username)
    u = User.one(username=username)
    if u is None:
        abort(404)
    else:
        user_id = User.one(username=username).id
        ms = Topic.all(user_id=user_id)
        ms.reverse()
        user_reply = Reply.all(user_id=user_id)
        rt = []
        for i in user_reply:
            t = Topic.one(id=i.topic_id)
            if t not in rt:
                rt.append(t)
            else:
                rt.remove(t)
                rt.append(t)
        rt.reverse()
        print(rt)
        return render_template('personal.html', user=u, ms=ms, rt=rt)


def not_found(e):
    return render_template('404.html')


@main.route('/image/add', methods=['POST'])
def avatar_add():
    file = request.files['avatar']

    # ../../root/.ssh/authorized_keys
    # filename = secure_filename(file.filename)
    suffix = file.filename.split('.')[-1]
    filename = '{}.{}'.format(str(uuid.uuid4()), suffix)
    path = os.path.join('images', filename)
    file.save(path)

    u = current_user()
    User.update(u.id, image='/images/{}'.format(filename))

    return redirect(url_for('.user_detail', username=u.username))


@main.route('/images/<filename>')
def image(filename):
    return send_from_directory('images', filename)


# def blueprint():
#     main = Blueprint('index', __name__)
#     main.route("/")(index)
#     main.route("/register", methods=['POST'])(register)
#     main.route("/login", methods=['POST'])(login)
#     main.route('/profile')(profile)
#     main.route('/user/<int:id>')(user_detail)
#
#     return main

@main.route('/setting')
def setting():
    u = current_user()
    token = new_csrf_token()
    return render_template('setting.html', token=token, user=u)


@main.route('/setting/username', methods=['POST'])
@csrf_required
def username_setting():
    form = request.form.to_dict()
    log('全部数据{}'.format(form))
    u = current_user()
    User.update(u.id, **form)
    # token = form['token']
    # csrf_tokens[token] = form['username']
    return redirect(url_for('.setting'))


@main.route('/setting/password', methods=['POST'])
@csrf_required
def password_setting():
    form = request.form.to_dict()
    u = current_user()
    log('第一次用户输出', u)
    if u.password == User.salted_password(form['old_pass']):
        new_pass = User.salted_password(form['new_pass'])
        form['password'] = new_pass
        log('传入的form', form)
        User.update(u.id, **form)
        u = current_user()
        log('第二次用户输出', u)
        return redirect(url_for('.setting'))
    else:
        return redirect(url_for('.index'))
