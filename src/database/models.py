# Third party imports
from sqlalchemy import Table, Column, Integer, String, Text, DateTime, Boolean, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()


# association table
# book_category = Table('book_category', Base.metadata,
#     Column('book_id', Integer, ForeignKey('books.id')),
#     Column('category_id', Integer, ForeignKey('categories.id'))
# )

# association table
video_category = Table('video_category', Base.metadata,
    Column('videolocal_id', Integer, ForeignKey('videolocal.id')),
    Column('category_id', Integer, ForeignKey('category.id')),
    PrimaryKeyConstraint('videolocal_id', 'category_id'),
)

class VideoSource(Base):
    __tablename__ = 'videosource'

    id = Column(Integer, primary_key=True)
    url = Column(String)

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __repr__(self):
        return "<VideoSource('%s','%s')>" % (self.name, self.url)


class VideoLocal(Base):
    __tablename__ = 'videolocal'

    id = Column(Integer, primary_key=True)
    title = Column(String)
    description = Column(Text)
    file_name = Column(String)
    web_url = Column(String)
    quality = Column(String)
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    video_id = Column(String)
    downloaded = Column(Boolean)
    video_length = Column(Integer)
    category = relationship("Category", secondary=video_category, backref='videolocal')
    option = relationship("VideoLocalOption", uselist=False, backref="videolocal")

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __repr__(self):
        return "<VideoLocal('%s','%s')>" % (self.title, self.url)

class VideoLocalOption(Base):
    __tablename__ = 'videolocaloption'
    id = Column(Integer, primary_key=True)
    video_id = Column(Integer, ForeignKey('videolocal.id'))
    uploaded = Column(Boolean, default = False)

    # def __init__(self, uploaded):
    #     self.uploaded = uploaded

class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String)

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __repr__(self):
        return "<Category('%s')>" % (self.name)