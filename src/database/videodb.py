# Standard library imports
import logging
import os

# Third party imports
from sqlalchemy import MetaData
from sqlalchemy import create_engine
from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker

# Local application imports
from database.models import Base
from config import Config

logger = logging.getLogger(__name__)
logger.setLevel("INFO")
db_log_file_name = 'db.log'
db_handler_log_level = logging.INFO

# db_handler = logging.FileHandler(db_log_file_name)
# db_handler.setLevel(db_handler_log_level)
# formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# db_handler.setFormatter(formatter)
db_logger = logging.getLogger('sqlalchemy')
# db_logger.addHandler(db_handler)
# db_logger.propagate = False
SQLITE = 'sqlite'


# Table Names

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


class FacebookVideoDatabase:
    DB_ENGINE = {
        'sqlite': 'sqlite:///{DB}'
    }

    # Main DB Connection Ref Obj
    db_engine = None

    def __init__(self, dbtype='sqlite', username='', password='', dbname='facebookvideo.db'):
        dbtype = dbtype.lower()
        logger.debug('dbtype is %s' % dbtype)
        if dbtype in self.DB_ENGINE.keys():
            db_path = os.path.join(Config.get_or_else('FOLDER', 'DB_DIR', '../db/'), dbname)
            engine_url = self.DB_ENGINE[dbtype].format(DB=db_path)
            logger.debug("engine_url is %s" % engine_url)
            self.db_engine = create_engine(engine_url, connect_args={'check_same_thread': False})
            logger.debug(self.db_engine)
            self.metadata = MetaData()
            Session = sessionmaker(bind=self.db_engine)
            self.session = Session()
            self.create_db_tables()
        else:
            print("DBType is not found in DB_ENGINE")

    def create_db_tables(self):
        try:
            Base.metadata.create_all(self.db_engine,checkfirst=True)
        except Exception as e:
            print("Error occurred during Table creation!")
            print(e)

    def insert_video_sources(self):
        from database.models import VideoSource
        sources = [
            VideoSource(name='McKatuReviewPhim', url=r"https://www.facebook.com/McKatuReviewPhim"),
            VideoSource(name='sedikitcinta2601/', url=r"https://www.facebook.com/watch/sedikitcinta2601/)")
        ]
        for _source in sources:
            if self.session.query(VideoSource).filter(VideoSource.url == _source.url).first() is None:
                self.session.add(_source)
        self.session.commit()

    def print_video_sources(self):
        from database.models import VideoSource
        results = self.session.query(VideoSource)
        for row in results:
            print(row)


if __name__ == "__main__":
    db = FacebookVideoDatabase(SQLITE, dbname='facebookvideo.db')
    db.create_db_tables()
    db.insert_video_sources()
    db.print_video_sources()
