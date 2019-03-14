from sqlalchemy import create_engine

import secret
from app import configured_app
from models.base_model import db
from models.topic import Topic
from models.user import User
from models.reply import Reply


def reset_database():
    url = 'mysql+pymysql://root:{}@localhost/?charset=utf8mb4'.format(secret.database_password)
    e = create_engine(url, echo=True)

    with e.connect() as c:
        c.execute('DROP DATABASE IF EXISTS bbs')
        c.execute('CREATE DATABASE bbs CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci')
        c.execute('USE bbs')

    db.metadata.create_all(bind=e)


def generate_fake_date():

    form = dict(
        username='guest',
        password='0723',
        signature='游客'
    )
    u = User.register(form)

    form = dict(
        username='nana',
        password='0723',
        signature='6666666'
    )
    u = User.register(form)


    with open('markdown_demo.md', encoding='utf8') as f:
        content = f.read()
    form = dict(
        title='markdown demo',
        content=content
    )
    Topic.add(form, u.id)


if __name__ == '__main__':
    app = configured_app()
    with app.app_context():
        reset_database()
        generate_fake_date()
