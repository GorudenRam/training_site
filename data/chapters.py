import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class Chapter(SqlAlchemyBase):
    __tablename__ = 'chapters'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    num = sqlalchemy.Column(sqlalchemy.Integer)
    title = sqlalchemy.Column(sqlalchemy.String)
    content = sqlalchemy.Column(sqlalchemy.String)
    course_id = sqlalchemy.Column(sqlalchemy.Integer,
                                  sqlalchemy.ForeignKey("courses.id"))
    html = sqlalchemy.Column(sqlalchemy.String)
    is_test = sqlalchemy.Column(sqlalchemy.Boolean)
    test_json = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    course = orm.relation('Course')

