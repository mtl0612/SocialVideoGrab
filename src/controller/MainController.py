from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtWidgets import QMainWindow, QApplication, QVBoxLayout, QHBoxLayout, QWidget, QSplitter

from ui.ui_main import Ui_MainWindow
from controller.AccountListController import AccountListController
from controller.VideoTableController import VideoTableController


class MainController(QMainWindow):
    def __init__(self, *args):
        super().__init__(*args)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        layout = QHBoxLayout()
        splitter1 = QSplitter(Qt.Horizontal)
        self.account_list_widget = AccountListController()
        splitter1.addWidget(self.account_list_widget)

        self.video_table_widget = VideoTableController()
        splitter1.addWidget(self.video_table_widget)
        splitter1.setSizes([100, 200])
        layout.addWidget(splitter1)

        widget = QWidget()
        widget.setLayout(layout)

        self.setCentralWidget(widget)