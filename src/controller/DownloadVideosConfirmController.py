import logging
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import QWidget, QDialog, QHeaderView, QTableWidgetItem

from ui.download_videos_confirm_dialog_ui import Ui_DownloadVideosConfirmDialog
from utils.misc import is_ms_time_format
logger = logging.getLogger(__name__)


class DownloadVideosConfirmController(QDialog):
    def __init__(self, video_dict, video_local_model, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ui = Ui_DownloadVideosConfirmDialog()
        self.ui.setupUi(self)
        self.ui.tableWidget.setRowCount(len(video_dict))
        self.ui.tableWidget.setColumnCount(4)
        self.ui.tableWidget.verticalHeader().setVisible(False)
        self.ui.tableWidget.setSortingEnabled(True)
        # self.ui.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.video_local_model = video_local_model

        header_labels = ['', 'VideoID', 'Link', 'Description', "Length"]
        self.ui.tableWidget.setHorizontalHeaderLabels(header_labels)

        row = 0
        video_ids = []
        for video_id in video_dict:
            if self.video_local_model.is_video_id_exists(video_id):
                continue

            logger.debug("video_id: %s", video_id)
            video_ids.append(video_id)
            videoid_item = QTableWidgetItem(video_id)
            # chkBoxItem.setText(video_id)
            videoid_item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            videoid_item.setCheckState(Qt.Checked)
            self.ui.tableWidget.setItem(row, 0, videoid_item)

            url_item = QTableWidgetItem(video_dict[video_id].get('url', ""))
            self.ui.tableWidget.setItem(row,1,url_item)

            text = video_dict[video_id].get('text', "")
            if not text:
                text = ""
            text_item = QTableWidgetItem(text)
            self.ui.tableWidget.setItem(row,2,text_item)

            video_length = video_dict[video_id].get('length', "")
            if is_ms_time_format(video_length):
                video_length = "00:" + video_length
            length_item = QTableWidgetItem(video_length)
            self.ui.tableWidget.setItem(row,3,length_item)

            row = row + 1

        self.ui.tableWidget.setRowCount(len(video_ids))
    def sizeHint(self) -> QSize:
        return QSize(50,100)

    def return_urls(self):
        return_urls = []
        logger.debug("self.ui.tableWidget.rowCount(): %s", self.ui.tableWidget.rowCount())
        for row in range(self.ui.tableWidget.rowCount()):

            logging.debug("row: %s", row)
            if self.ui.tableWidget.item(row, 0).checkState():
                return_urls.append(self.ui.tableWidget.item(row, 1).text())
        return return_urls

    @staticmethod
    def get_confirmation(model = None, parent=None, ):
        dialog = DownloadVideosConfirmController(model, parent)
        ok = dialog.exec_()
        if ok:
            return_urls = dialog.return_urls()
            return (return_urls, ok)
        else:
            return (None, ok)