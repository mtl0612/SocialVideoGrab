
from PyQt5.QtCore import QAbstractTableModel, Qt, QVariant

from database import videodb
from database.models import VideoSource, VideoLocal



class VideoSourceQtModel(QAbstractTableModel):
    db = videodb.FacebookVideoDatabase(dbname=r'facebookvideo.db')
    def __init__(self, parent, header, *args):
        QAbstractTableModel.__init__(self, parent, *args)
        # 5. fetch data

        results = self.db.session.query(VideoSource).all()
        self.mylist = results
        self.header = header

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

class VideoLocalQtModel(QAbstractTableModel):
    db = videodb.FacebookVideoDatabase(dbname=r'facebookvideo.db')
    def __init__(self, parent, header, *args):
        QAbstractTableModel.__init__(self, parent, *args)
        # 5. fetch data

        results = self.db.session.query(VideoLocal).all()
        self.mylist = results
        self.header = header

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
