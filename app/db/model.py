from sqlalchemy import Column, String, Integer, ForeignKey, Boolean, Time, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from sqlalchemy.dialects.sqlite import DATETIME

from app.db import Base


class User(Base):
    __tablename__ = 'users'
    id          = Column(Integer, primary_key=True)
    cookie_id   = Column(String, nullable=False)
    os          = Column(String, nullable=True)
    browser     = Column(String, nullable=True)
    mobile      = Column(Boolean, nullable=True)
    screen_size = Column(String, nullable=True)
    user_agent  = Column(String, nullable=True)
    annotations = relationship('Annotation', backref='user', lazy=True)

    def __init__(self, cookie_id, os=None, browser=None, mobile=None, screen_size=None, user_agent=None):
        self.cookie_id   = cookie_id
        self.os          = os
        self.browser     = browser
        self.mobile      = mobile
        self.screen_size = screen_size
        self.user_agent  = user_agent


class Page(Base):
    __tablename__ = 'pages'
    id    = Column(Integer, primary_key=True)
    path  = Column(String)
    crops = relationship('Crop', backref='pages', lazy=True)

    def __init__(self, path):
        self.path = path


class Crop(Base):
    __tablename__ = 'crops'
    id      = Column(Integer, primary_key=True)
    page_id = Column(String, ForeignKey('pages.id'), nullable=False)
    x       = Column(Integer)
    y       = Column(Integer)
    width   = Column(Integer)
    height  = Column(Integer)
    cropped = Column(Boolean)

    def __init__(self, page_id, x, y, width, height, cropped=False):
        self.page_id = page_id
        self.x       = x
        self.y       = y
        self.width   = width
        self.height  = height
        self.cropped = cropped


class Annotation(Base):
    __tablename__ = 'annotations'
    id              = Column(Integer, primary_key=True)
    user_id         = Column(Integer, ForeignKey('users.id'), nullable=False)
    record_id       = Column(Integer, ForeignKey('records.id'), nullable=False)
    annotation      = Column(String)
    annotation_time = Column(Time())
    timestamp       = Column(DATETIME(truncate_microseconds=3), nullable=False, default=func.now())

    def __init__(self, user_id, record_id, annotation, annotation_time):
        self.user_id         = user_id
        self.record_id       = record_id
        self.annotation      = annotation
        self.annotation_time = annotation_time


class Set(Base):
    __tablename__ = 'sets'
    id          = Column(Integer, primary_key=True)
    type        = Column(Integer)
    name        = Column(String)
    active      = Column(Boolean)
    description = Column(String)
    records     = relationship('Record', backref='set', lazy=True)
    #annotations = relationship('Annotation', backref='set', lazy=True)

    def __init__(self, type, name, active, description):
        self.type        = type
        self.name        = name
        self.active      = active
        self.description = description


class Record(Base):
    __tablename__ = 'records'
    id          = Column(Integer, primary_key=True)
    position    = Column(Float)
    set_id      = Column(Integer, ForeignKey('sets.id'), nullable=False)
    annotations = relationship('Annotation', backref='record', lazy=True)

    def __init__(self, position, set_id):
        self.position = position
        self.set_id   = set_id


class RecordCrop(Base):
    __tablename__ = 'record_crops'
    id        = Column(Integer, primary_key=True)
    crop_id   = Column(Integer, ForeignKey('crops.id'))
    record_id = Column(Integer, ForeignKey('records.id'))
    order     = Column(Integer)

    def __init__(self, crop_id, ann_record_id, order):
        self.crop_id   = crop_id
        self.record_id = ann_record_id
        self.order     = order
