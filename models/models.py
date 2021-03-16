from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from models.database import Base


class Words(Base):
    __tablename__ = 'words'
    id = Column(Integer, primary_key=True)
    vocabulary = Column(String(128))
    date = Column(String(128))
    uuid = Column(String(128))

    def __init__(self, vocabulary=None, date=None, uuid=None):
        self.vocabulary = vocabulary
        self.date = date
        self.uuid = uuid



