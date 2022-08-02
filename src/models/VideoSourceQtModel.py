# Standard library imports
import logging

# Third party imports
from PyQt5.QtCore import QAbstractTableModel, Qt, QVariant, pyqtSignal

# Local application imports
from database import videodb
from database.models import VideoSource

logger = logging.getLogger(__name__)


class VideoSourceQtModel(QAbstractTableModel):
    db = videodb.FacebookVideoDatabase(dbname=r'facebookvideo.db')

    videoSourceAddedSignal = pyqtSignal(object)

    def __init__(self, parent, *args):
        QAbstractTableModel.__init__(self, parent, *args)
        # 5. fetch data

        results = self.db.session.query(VideoSource).all()
        self.mylist = results

        self.header = ['id', 'url']

        self.videoSourceAddedSignal.connect(self.add_source)

    def _update_model_data(self):
        self.beginResetModel()
        results = self.db.session.query(VideoSource).all()

        self.mylist = results
        self.endResetModel()

    def rowCount(self, parent):
        return len(self.mylist)

    def columnCount(self, parent):
        return len(self.header)

    def data(self, index, role):
        # 5. populate data
        if not index.isValid():
            return None
        if (role == Qt.DisplayRole):
            return getattr(self.mylist[index.row()],self.header[index.column()])
        else:
            return QVariant()

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.header[col]
        return None

    def get_url(self, index: int):
        if index < len(self.mylist):
            return self.mylist[index].url
        else:
            return ""

    def add_source(self, url: str):
        if not self.check_page_exists(url):
            video_source = VideoSource(url = url)
            self.db.session.add(video_source)
            self.db.session.commit()
            self._update_model_data()

    def check_page_exists(self, url: str):
        url_existed = self.db.session.query(VideoSource).filter(VideoSource.url == url).first() is not None
        return url_existed