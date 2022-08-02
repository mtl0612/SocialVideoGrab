from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QWidget

from ui.account_list_widget_ui import Ui_AccountListWidget

class AccountListController(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ui = Ui_AccountListWidget()
        self.ui.setupUi(self)

    def sizeHint(self) -> QSize:
        return QSize(50,100)