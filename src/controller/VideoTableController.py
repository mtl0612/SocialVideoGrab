from PyQt5.QtCore import Qt, pyqtSlot, QSize
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QSizePolicy, QLabel, QPushButton

from ui.ui_video_table_widget import Ui_VideoTableWidget
from models.QtModel import VideoSourceQtModel, VideoLocalQtModel

class VideoTableController(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ui = Ui_VideoTableWidget()
        self.ui.setupUi(self)
        header = ['title', 'description', 'file_name', 'web_url', 'time_created']
        self.table_model = VideoLocalQtModel(self, header)
        self.ui.tableView.setModel(self.table_model)


    def sizeHint(self) -> QSize:
        return QSize(500,600)
