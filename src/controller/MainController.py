#!/usr/bin/env python3
# Standard library imports
import re
import logging
import time
import random
from enum import Enum

# Third party imports
from PyQt5.QtCore import Qt, pyqtSignal, QThread
from PyQt5.QtWidgets import QMainWindow, QHBoxLayout, QWidget, QSplitter, QInputDialog, QProgressBar, QStatusBar, QLabel

# Local application imports
from ui.main_ui import Ui_MainWindow
from controller.CategoryController import CategoryController
from controller.VideoTableController import VideoTableController
from controller.PageUrlInputController import PageUrlInputController
from controller.NewCategoryController import NewCategoryController
from controller.DownloadVideosConfirmController import DownloadVideosConfirmController
from thread.Worker import Worker
from models.VideoSourceQtModel import VideoSourceQtModel
from models.VideoLocalQtModel import VideoLocalQtModel
from models.CategoryQtModel import CategoryQtModel

from utils.facebook_download import download_fb_video, get_video_pages_from_fb_page
from config import Config
from utils.misc import validate_url

logger = logging.getLogger(__name__)

class Status(Enum):
    DOWNLOAD_IN_PROGRESS = 1
    IDLE = 2

class MainController(QMainWindow):
    sig_download_in_progress = pyqtSignal()
    sig_download_finished = pyqtSignal()

    sig_new_category_input = pyqtSignal()
    sig_apply_category_filter = pyqtSignal(str)
    sig_confirm_download_videos = pyqtSignal(dict)

    def __init__(self, *args):
        super().__init__(*args)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.video_local_model = VideoLocalQtModel(parent = None)
        self.video_source_model = VideoSourceQtModel(parent = None)
        self.category_model = CategoryQtModel(parent = None)

        layout = QHBoxLayout()
        splitter1 = QSplitter(Qt.Horizontal)
        self.video_category_widget = CategoryController(parent = self, model = self.category_model)
        splitter1.addWidget(self.video_category_widget)

        self.video_table_widget = VideoTableController(parent = self, model = self.video_local_model, \
                                                       category_model=self.category_model)
        splitter1.addWidget(self.video_table_widget)
        splitter1.setStretchFactor(0,1)
        splitter1.setStretchFactor(1,4)
        layout.addWidget(splitter1)

        widget = QWidget()
        widget.setLayout(layout)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        self.label = QLabel()
        self.label.setText("Idle")

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 1)

        self.status_bar.addWidget(self.label)
        self.status_bar.addPermanentWidget(self.progress_bar)
        self.setCentralWidget(widget)

        self.ui.action_hide_failed_videos.setCheckable(True)

        self.stopFlag = False
        self._hide_failed_videos = True

        self.ui.action_hide_failed_videos.setChecked(self._hide_failed_videos)
        self.video_table_widget.hide_failed_videos(self._hide_failed_videos)

        self._connect_actions()

    def _connect_actions(self):

        self.sig_download_in_progress.connect(lambda: self.update_menu(Status.DOWNLOAD_IN_PROGRESS))
        self.sig_download_in_progress.connect(lambda: self.update_status_bar(Status.DOWNLOAD_IN_PROGRESS))
        self.sig_download_finished.connect(lambda: self.update_menu(Status.IDLE))
        self.sig_download_finished.connect(lambda: self.update_status_bar(Status.IDLE))

        self.sig_download_finished.connect(lambda: setattr(self, 'stopFlag', False))

        self.ui.action_download_video.triggered.connect(self.confirm_download_video)
        self.ui.action_download_videos.triggered.connect(self.page_video_input)
        self.sig_confirm_download_videos.connect(self.confirm_download_videos)

        self.ui.action_stop_download.triggered.connect(lambda: setattr(self, 'stopFlag', True))

        self.ui.action_hide_failed_videos.triggered.connect(self.toggle_show_failed_videos)
        self.ui.action_hide_failed_videos.triggered.connect(
            lambda: self.video_table_widget.hide_failed_videos(self._hide_failed_videos))

        self.sig_new_category_input.connect(self.show_new_category_dialog)

        self.sig_apply_category_filter.connect(self.video_local_model.sig_apply_category_filter)

    def toggle_show_failed_videos(self):
        self._hide_failed_videos = not self._hide_failed_videos
        self.ui.action_hide_failed_videos.setChecked(self._hide_failed_videos)

    def start_fn_in_thread(self, fn, *args, **kwargs):
        self.thread = QThread(parent=self)
        self.worker = Worker(fn, *args, **kwargs)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()

    def update_menu(self, status):
        if status == Status.DOWNLOAD_IN_PROGRESS:
            self.ui.action_download_video.setDisabled(True)
            self.ui.action_download_videos.setDisabled(True)
            self.ui.action_stop_download.setDisabled(False)
        elif status == Status.IDLE:
            self.ui.action_download_video.setDisabled(False)
            self.ui.action_download_videos.setDisabled(False)
            self.ui.action_stop_download.setDisabled(True)

    def update_status_bar(self, status):
        if status == Status.DOWNLOAD_IN_PROGRESS:
            self.progress_bar.setRange(0,0)
            self.progress_bar.show()
            self.label.setText("Downloading......")
        elif status == Status.IDLE:
            self.progress_bar.setRange(0, 1)
            self.progress_bar.hide()
            self.label.setText("Idle")

    def confirm_download_video(self):
        url, ok = QInputDialog.getText(self, 'input dialog', 'Please enter URL:', \
                                       text=r"https://www.facebook.com/phimmmmgofim/videos/352830069069376/")
        if ok and validate_url(url):
            self.start_fn_in_thread(self.download_single_video, url)

    def download_single_video(self, url):
        if self.video_table_widget.table_model.check_video_exists(url):
            return

        logger.info("Start download video from %s" % url)
        self.sig_download_in_progress.emit()
        res_video = download_fb_video(url)
        if res_video is not None:
            self.video_table_widget.table_model.videoAddedSignal.emit(res_video)
        self.sig_download_finished.emit()
        logger.debug("Function download_single_video stopped!")

    def page_video_input(self):
        page_url, download_all, ok = PageUrlInputController.get_data(model=self.video_source_model)
        if ok and validate_url(page_url):
            logging.debug("page_url inputed: %s", page_url)
            self.video_source_model.videoSourceAddedSignal.emit(page_url)
            self.start_fn_in_thread(self.fetch_video_links, page_url, download_all)

    def fetch_video_links(self, page_url, download_all = True):
        if re.fullmatch("https://www.facebook.com/[\w\d\-\.]+", page_url.rstrip("/")):
            page_url = page_url.rstrip("/") + "/videos/?ref=page_internal"

        logger.info("Start download videos from %s" % page_url)
        self.sig_download_in_progress.emit()
        video_urls = get_video_pages_from_fb_page(page_url, download_all = download_all)
        if video_urls:
            self.sig_confirm_download_videos.emit(video_urls)
        else:
            self.sig_download_finished.emit()

    def confirm_download_videos(self, video_dicts):
        download_urls,ok = DownloadVideosConfirmController.get_confirmation(video_dicts, self.video_local_model)
        if ok:
            # logger.debug("download_urls: %s", download_urls)
            self.start_fn_in_thread(self.download_videos, download_urls)

    def download_videos(self, video_urls):
        for url in video_urls:
            if self.video_table_widget.table_model.check_video_exists(url):
                continue
            res_video = download_fb_video(url)
            if res_video is not None:
                self.video_table_widget.table_model.videoAddedSignal.emit(res_video)
                MIN_DELAY = Config.getfloat_or_else('DOWNLOAD', 'MIN_DELAY', 60)
                MAX_DELAY = Config.getfloat_or_else('DOWNLOAD', 'MAX_DELAY', 120)
                sleep_time = random.randint(MIN_DELAY, MAX_DELAY)
                logger.info("Sleeping for %s second....", sleep_time)
                for _ in range(sleep_time):
                    time.sleep(1)
                    if self.stopFlag:
                        self.sig_download_finished.emit()
                        logger.debug("Function download_page_videos stopped!")
                        return

        self.sig_download_finished.emit()
        logger.debug("Function download_page_videos stopped!")

    def show_new_category_dialog(self):
        category_name, ok = NewCategoryController.get_str()
        if ok:
            logging.debug("category_name inputed: %s", category_name)
            self.category_model.sig_add_category.emit(category_name)