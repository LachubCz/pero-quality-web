from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

from app.db.model import User, Annotation, Crop, Page, Record, Set, RecordCrop
