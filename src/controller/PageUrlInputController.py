import logging
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import QWidget, QDialog

from models.VideoSourceQtModel import VideoSourceQtModel
from ui.page_url_input_dialog_ui import Ui_PageUrlInputDialog
from utils.misc import validate_url

logger = logging.getLogger(__name__)


class PageUrlInputController(QDialog):
    def __init__(self, model = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ui = Ui_PageUrlInputDialog()
        self.ui.setupUi(self)

        if model is not None:
            self.model = model
            self.ui.comboBox.setModel(self.model)
            self.ui.comboBox.setModelColumn(1)

        self.text = ""
        self.ui.comboBox.currentTextChanged.connect(self.set_current_text)
        self.ui.comboBox.activated.connect(self.set_combobox_text)
        self.set_combobox_text(0)

    def set_combobox_text(self, index: int):
        text = self.model.get_url(index)
        self.ui.comboBox.setCurrentText(text)

    def set_current_text(self, text):
        self.text = self.ui.comboBox.currentText()

    def sizeHint(self) -> QSize:
        return QSize(50,100)

    def return_string(self):
        return str(self.text)

    def is_download_all(self):
        return self.ui.checkDownloadAll.checkState()
    @staticmethod
    def get_data(model = None):
        dialog = PageUrlInputController(model)
        ok = dialog.exec_()
        if ok:
            return_text = dialog.return_string()
            download_all = dialog.is_download_all()
            return (return_text,download_all, ok)
        else:
            return (None,None, ok)