from flask import (
    render_template,
    request,
    redirect,
    url_for,
    Blueprint,
)

from routes import current_user

from models.topic import Topic

from routes import csrf_required

main = Blueprint('my_topic', __name__)


@main.route("/")
def index():
    ms = Topic.all()
    u = current_user()
    print(u)
    # if u == None:
    #     u = 'guest'
    return render_template("topic/index.html", ms=ms, user=u)


@main.route('/<int:id>')
# /topic/1
# @main.route('/')
# /topic?id=1
def detail(id):
    # id = int(request.args['id'])
    # http://localhost:3000/topic/1
    m = Topic.get(id)

    # 传递 topic 的所有 reply 到 页面中
    return render_template("topic/detail.html", topic=m)


@main.route("/add", methods=["POST"])
def add():
    form = request.form.to_dict()
    u = current_user()
    m = Topic.add(form, user_id=u.id)
    return redirect(url_for('.detail', id=m.id))


@main.route("/new")
def new():
    return render_template("topic/new.html")


# @main.route("/delete")
# def delete():
#     # form = request.form.to_dict()
#     u = current_user()
#     m = Topic.delete(user_id=u.id)
#     return redirect(url_for('.index'))

@main.route("/delete")
@csrf_required
# @login_required
def delete():
    id = int(request.args.get('id'))
    u = current_user()
    print('删除 topic 用户是', u, id)
    Topic.delete(id)
    return redirect(url_for('.index'))
