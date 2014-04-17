#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sqlalchemy

from sqlalchemy import Column, Integer, ForeignKey, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from config import DB_PATH


Base = declarative_base()


class Post(Base):
    __tablename__ = 'posts'
    id = Column(Integer, primary_key=True)
    post_id = Column(Integer)
    lepra_post_id = Column(Integer)
    reddit_post_id = Column(String(255))


class Comment(Base):
    __tablename__ = 'comments'
    id = Column(Integer, primary_key=True)
    post_id = Column(Integer, ForeignKey('posts.id'))
    post = relationship(Post)
    lepra_comment_id = Column(Integer, unique=True)
    reddit_comment_id = Column(String(20))
    author = Column(String(255))
    comment = Column(Text())
    youtube_url = Column(String(255))
    rating = Column(Integer)


if __name__ == '__main__':
    # initdb
    engine = sqlalchemy.create_engine(DB_PATH)
    Base.metadata.create_all(engine)

    """
    INSERT INTO posts (post_id, lepra_post_id, reddit_post_id) VALUES (100, 1709850, '236vkf');
    """
