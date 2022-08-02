# Standard library imports
import logging
from enum import Enum

# Third party imports
from PyQt5.QtCore import QAbstractTableModel, Qt, QVariant, pyqtSignal

# Local application imports
from database import videodb
from database.models import Category

logger = logging.getLogger(__name__)

class CategoryLabel(Enum):
    ALL = 1
    UNCATEGORIZED = 2

class CategoryQtModel(QAbstractTableModel):
    db = videodb.FacebookVideoDatabase(dbname=r'facebookvideo.db')

    sig_add_category = pyqtSignal(str)

    def __init__(self, parent, *args):
        QAbstractTableModel.__init__(self, parent, *args)
        # 5. fetch data

        results = self.db.session.query(Category).all()

        self.mylist = results
        self.header = ['id', 'name']

        self._connect_actions()

    def _connect_actions(self):
        self.sig_add_category.connect(self.add_category)

    def _update_model_data(self):
        self.beginResetModel()
        results = self.db.session.query(Category).all()

        self.mylist = results
        self.endResetModel()

    def rowCount(self, parent):
        return len(self.mylist) + 2

    def columnCount(self, parent):
        return len(self.header)

    def data(self, index, role):
        # 5. populate data
        if not index.isValid():
            return None
        if (role == Qt.DisplayRole):
            row = index.row()
            if row == 0:
                return "All"
            elif row == 1:
                return "Uncategorized"
            else:
                return getattr(self.mylist[row-2],self.header[index.column()])
        else:
            return QVariant()


    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.header[col]
        return None

    def get_all_categories(self):
        return [category.name for category in self.mylist]

    def add_category(self, name: str):
        if not self.check_category_exists(name):
            category = Category(name = name)
            self.db.session.add(category)
            self.db.session.commit()
            self._update_model_data()

    def check_category_exists(self, name: str):
        if name.lower() in ["all", "uncategorized"]:
            return True
        url_existed = self.db.session.query(Category).filter(Category.name == name).first() is not None
        return url_existed