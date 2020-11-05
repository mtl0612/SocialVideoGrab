from PyQt5.QtWidgets import QApplication, QWidget, QTableView, QAbstractItemView, QVBoxLayout

from QtModel import VideoSourceQtModel, VideoLocalQtModel

from widget.accountListWidget import Ui_Form as AccountListWidget
from widget.VideoTableWidget import Ui_Form as VideoTableWidget

class VideoSourceWidget(QWidget):
    def __init__(self, header, *args):
        QWidget.__init__(self, *args)
        self.setWindowTitle("Video Source TableView")

        self.table_model = VideoSourceQtModel(self, header)
        self.table_view = QTableView()
        self.table_view.setModel(self.table_model)
        layout = QVBoxLayout(self)
        layout.addWidget(self.table_view)
        self.setLayout(layout)

class VideoLocalWidget(QWidget):
    def __init__(self, header, *args):
        QWidget.__init__(self, *args)
        self.setWindowTitle("Video Local TableView")

        self.table_model = VideoLocalQtModel(self, header)
        self.table_view = QTableView()
        self.table_view.setModel(self.table_model)
        layout = QVBoxLayout(self)
        layout.addWidget(self.table_view)
        self.setLayout(layout)

if __name__ == '__main__':
    print("Start...")
    app = QApplication([])
    # header = ['name', 'url']
    # win = VideoSourceWidget(header)
    header = ['title', 'description', 'file_name', 'web_url', 'time_created']
    win = VideoLocalWidget(header)
    print("Start showing windows...")
    win.show()
    app.exec_()
    print("Finished!")