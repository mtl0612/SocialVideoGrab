import logging
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import QWidget, QDialog

from ui.new_category_name_dialog_ui import Ui_Dialog

logger = logging.getLogger(__name__)


class NewCategoryController(QDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.ui.buttonBox.accepted.connect(self.accept)
        self.ui.buttonBox.rejected.connect(self.reject)

    def sizeHint(self) -> QSize:
        return QSize(50, 100)
    def return_string(self):
        return str(self.ui.lineEdit.text())

    @staticmethod
    def get_str(parent=None, ):
        dialog = NewCategoryController(parent)
        ok = dialog.exec_()
        return_text = dialog.return_string()
        return (return_text, ok)