# Third party imports
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


# association table
# book_category = Table('book_category', Base.metadata,
#     Column('book_id', Integer, ForeignKey('books.id')),
#     Column('category_id', Integer, ForeignKey('categories.id'))
# )

class VideoSource(Base):
    __tablename__ = 'videosource'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    url = Column(String)

    def __repr__(self):
        return "<VideoSource('%s','%s')>" % (self.name, self.url)


class VideoLocal(Base):
    __tablename__ = 'videolocal'

    id = Column(Integer, primary_key=True)
    title = Column(String)
    description = Column(Text)
    file_name = Column(String)
    web_url = Column(String)
    time_created = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return "<VideoLocal('%s','%s')>" % (self.title, self.url)
