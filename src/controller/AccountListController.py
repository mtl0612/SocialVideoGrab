from PyQt5.QtCore import Qt, pyqtSlot, QSize
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget

from ui.ui_account_list_widget import Ui_AccountListWidget

class AccountListController(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ui = Ui_AccountListWidget()
        self.ui.setupUi(self)

    def sizeHint(self) -> QSize:
        return QSize(50,100)