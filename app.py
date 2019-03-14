import time

from flask import Flask
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

import config
import secret
from models.base_model import db
from models.reply import Reply
from models.topic import Topic
from models.user import User
from routes import index
from utils import log

from routes.index import main as index_routes
from routes.topic import main as topic_routes
from routes.reply import main as reply_routes
from routes.index import not_found


def count(input):
    log('count using jinja filter')
    return len(input)


def format_time(unix_timestamp):
    f = '%Y-%m-%d %H:%M:%S'
    value = time.localtime(unix_timestamp)
    formatted = time.strftime(f, value)
    return formatted


def configured_app():
    app = Flask(__name__)
    app.secret_key = secret.secret_key

    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:{}@localhost/bbs?charset=utf8mb4'.format(
        secret.database_password
    )
    db.init_app(app)

    app.register_blueprint(index_routes)
    app.register_blueprint(topic_routes, url_prefix='/topic')
    app.register_blueprint(reply_routes, url_prefix='/reply')

    app.template_filter()(count)
    app.template_filter()(format_time)
    app.errorhandler(404)(not_found)

    admin = Admin(app, name='bbs', template_mode='bootstrap3')
    admin.add_view(ModelView(User, db.session))
    admin.add_view(ModelView(Topic, db.session))
    admin.add_view(ModelView(Reply, db.session))
    # Add administrative views here

    return app


if __name__ == '__main__':
    app = configured_app()
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.jinja_env.auto_reload = True
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    config = dict(
        debug=True,
        host='localhost',
        port=2000,
    )
    app.run(**config)
