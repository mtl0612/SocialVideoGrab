import logging

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import QWidget

from ui.video_category_widget_ui import Ui_VideoCategoryWidget
from models.CategoryQtModel import CategoryQtModel

logger = logging.getLogger(__name__)

class CategoryController(QWidget):
    def __init__(self, parent = None, model = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ui = Ui_VideoCategoryWidget()
        self.ui.setupUi(self)

        if parent:
            self.parent = parent

        if model:
            self.model = model
        else:
            self.model = CategoryQtModel(self)

        self.ui.listView.setModel(self.model)
        self.ui.listView.setModelColumn(1)
        self.ui.listView.setContextMenuPolicy(Qt.CustomContextMenu)

        self._connect_actions()

    def _connect_actions(self):
        self.selModel = self.ui.listView.selectionModel()
        self.selModel.selectionChanged.connect(self.on_row_selection_changed)

    def on_row_selection_changed(self, current, previous):
        indexes = current.indexes()
        # Only apply filter using first row
        index = indexes[0]
        category = self.model.data(index = index, role = Qt.DisplayRole)
        self.parent.sig_apply_category_filter.emit(category)

    def sizeHint(self) -> QSize:
        return QSize(50,100)

