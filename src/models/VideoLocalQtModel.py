# Standard library imports
import logging
import os
import webbrowser
import subprocess
from pathlib import Path
from datetime import timezone

# Third party imports
from PyQt5.QtCore import QAbstractTableModel, Qt, QVariant, pyqtSignal, QSize

# Local application imports
from database import videodb
from database.models import VideoSource, VideoLocal, Category, video_category, VideoLocalOption
from config import Config
from utils.misc import addToClipBoard, parse_fb_video_id, remove_non_ascii, get_video_length, video_length_repr
from models.common import Header

logger = logging.getLogger(__name__)


class VideoLocalQtModel(QAbstractTableModel):
    db = videodb.FacebookVideoDatabase(dbname=r'facebookvideo.db')

    videoAddedSignal = pyqtSignal(object)
    removeVideosSignal = pyqtSignal(list)
    deleteRowsSignal = pyqtSignal(list)
    copyVideoPathSignal = pyqtSignal(int)
    copyVideoDescriptionSignal = pyqtSignal(int)
    copyVideoSourceUrlSignal = pyqtSignal(int)
    openWebUrlSignal = pyqtSignal(int)
    showOnlyDownloadedVideosSignal = pyqtSignal(bool)

    sig_add_videos_to_category = pyqtSignal(list, str)
    sig_apply_category_filter = pyqtSignal(str)
    sig_open_in_explorer = pyqtSignal(int)

    # dataChanged = pyqtSignal()

    def __init__(self, parent, *args):
        QAbstractTableModel.__init__(self, parent = None, *args)
        # 5. fetch data
        self.show_only_downloaded = False
        self._category = "All"
        self._update_model_data()

        self.headers = [Header('video_number', 'No.', 50),
                   Header('title', 'Title', 300),
                   Header('description', 'Description', 300),
                   Header('uploaded', 'Uploaded?', 70),
                   # Header('file_name', 'File name', 300),
                   Header('video_length', 'Length', 60),
                   # Header('web_url', 'Url', 100),
                   Header('time_created', 'Time created', 150),
                   Header('quality', 'Quality', 60),
                   Header('video_id', 'Video ID', 150),
                   Header('downloaded', 'Downloaded?', 100),

                   ]
        self._connect_actions()

    def _connect_actions(self):
        self.videoAddedSignal.connect(self.add_video)
        self.removeVideosSignal.connect(self.remove_videos)
        self.deleteRowsSignal.connect(self.delete_rows)
        self.copyVideoPathSignal.connect(self.copy_video_path)
        self.copyVideoDescriptionSignal.connect(self.copy_video_description)
        self.copyVideoSourceUrlSignal.connect(self.copy_video_source_url)
        self.openWebUrlSignal.connect(self.open_web_url)
        self.showOnlyDownloadedVideosSignal.connect(self.set_show_only_downloaded)
        self.sig_add_videos_to_category.connect(self.add_videos_to_category)
        self.sig_apply_category_filter.connect(self.filter_by_category)
        self.sig_open_in_explorer.connect(self.open_in_explorer)

    def _update_model_data(self):
        self.beginResetModel()
        if (self._category is None) or self._category == "All":
            query = self.db.session.query(VideoLocal)
        elif self._category == "Uncategorized":
            # query = self.db.session.query(VideoLocal) \
            #          .outerjoin(video_category, video_category.videolocal_id == VideoLocal.id)
            query = self.db.session.query(VideoLocal).filter(~VideoLocal.category.any())
        else:
            query = self.db.session.query(VideoLocal).filter(VideoLocal.category.any(name=self._category))

        if self.show_only_downloaded:
            results = query.filter(VideoLocal.downloaded).all()
        else:
            results = query.all()

        self.video_data = results
        self.endResetModel()

    def rowCount(self, parent):
        return len(self.video_data)

    def columnCount(self, parent):
        return len(self.headers)

    def data(self, index, role):
        # 5. populate data
        if not index.isValid():
            return None
        if role == Qt.DisplayRole:
            header = self.headers[index.column()]

            # if header is datetime type, convert to local time zone before return
            if header.name == "time_created":
                time_created_utc = getattr(self.video_data[index.row()], header.name)
                time_create_local = time_created_utc.replace(tzinfo=timezone.utc).astimezone(tz=None)
                return str(time_create_local.strftime("%Y-%m-%d %H:%M:%S"))

            # if header is video_number, return video number
            if header.name == "video_number":
                return index.row()+1
            if header.name == "description":
                description = getattr(self.video_data[index.row()], header.name)
                description = description.replace("\n", " ")
                return description[:50]
            if header.name == "video_length":
                video_length = getattr(self.video_data[index.row()], header.name)
                return video_length_repr(video_length)
            if header.name == "uploaded":
                return ""
            # default
            cell = getattr(self.video_data[index.row()], header.name)
            if cell is not None:
                return str(cell)
            else:
                return ""
        elif role == Qt.CheckStateRole:
            header = self.headers[index.column()]
            if header.name == "uploaded":
                video = self.video_data[index.row()]
                if (video.option) is not None and video.option.uploaded:
                    return Qt.Checked
                else:
                    return Qt.Unchecked
            else:
                return QVariant()
        else:
            return QVariant()

    def setData(self, index, value, role):
        if not index.isValid():
            return False
        logger.debug("Set data")
        if (role == Qt.CheckStateRole):
            header = self.headers[index.column()]
            if header.name == "uploaded":
                video = self.video_data[index.row()]
                if video.option is None:
                    option = VideoLocalOption()
                    video.option = option
                if value == Qt.Checked:
                    video.option.uploaded = True
                else:
                    video.option.uploaded = False
                self.db.session.commit()
                return True
        else:
            return False

    def flags(self, index):
        if not index.isValid():
            return False
        fl = QAbstractTableModel.flags(self, index)

        header = self.headers[index.column()]
        if header.name == "uploaded":
            fl |= Qt.ItemIsEditable | Qt.ItemIsUserCheckable
        return fl

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.SizeHintRole:
            header = self.headers[col]
            return QSize(header.width, 20)
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            header = self.headers[col]
            return header.title
        return None

    def add_video(self, video):
        logger.debug("video: %s", remove_non_ascii(str(video)))
        video_new = VideoLocal(**video)
        self.db.session.add(video_new)
        self.db.session.commit()
        self._update_model_data()

    def remove_videos(self, rows: list):
        logger.debug("function remove_videos started!")
        for row in rows:
            video = self.video_data[row]
            if video.downloaded:
                file_name = video.file_name
                VIDEO_DIR = Path(Config.get_or_else('FOLDER', 'VIDEO_DIR', '../videos'))
                video_path = VIDEO_DIR / file_name
                try:
                    os.remove(video_path)
                    logger.info("%s removed successfully" % video_path)
                except OSError as error:
                    logger.warning(error)
                    logger.warning("File path can not be removed")
            video.downloaded = False
            video.file_name = None
            self.db.session.commit()

        self._update_model_data()
        logger.debug("function remove_videos finished!")

    def delete_rows(self, rows: list):
        for row in rows:
            video = self.video_data[row]
            if video.downloaded:
                file_name = video.file_name
                VIDEO_DIR = Path(Config.get_or_else('FOLDER', 'VIDEO_DIR', '../videos'))
                video_path = VIDEO_DIR/file_name
                try:
                    os.remove(video_path)
                    logger.info("%s removed successfully" % video_path)
                except OSError as error:
                    logger.warning(error)
                    logger.warning("File path can not be removed")

            self.db.session.delete(self.video_data[row])
            self.db.session.commit()

        self._update_model_data()

    def get_full_video_path(self, file_name):
        VIDEO_DIR = Path(Config.get_or_else('FOLDER', 'VIDEO_DIR', '../videos'))
        video_path = VIDEO_DIR/file_name
        return video_path

    def get_video_path(self, row: int):
        file_name = self.video_data[row].file_name
        if file_name is None:
            return
        VIDEO_DIR = Path(Config.get_or_else('FOLDER', 'VIDEO_DIR', '../videos'))
        video_path = VIDEO_DIR/file_name
        return video_path

    def copy_video_path(self, row: int):
        video_path = self.get_video_path(row)
        addToClipBoard(str(video_path))

    def copy_video_description(self, row: int):
        description = self.video_data[row].description
        APPEND_TEXT = Config.get_or_else('UPLOAD', 'APPEND_TEXT', "")
        description += "\n" + APPEND_TEXT
        addToClipBoard(description)

    def copy_video_source_url(self, row: int):
        url = self.video_data[row].web_url
        addToClipBoard(url)

    def open_web_url(self, row: int):
        webbrowser.open(self.video_data[row].web_url)  # Go to example.com

    def open_in_explorer(self, row:int):
        video_path = self.get_video_path(row)
        subprocess.Popen(r'explorer /select,"%s"'%video_path)

    def check_video_exists(self, url: str):
        url_existed_cond1 = self.db.session.query(VideoLocal).filter(VideoLocal.web_url == url).first() is not None
        video_id = parse_fb_video_id(url)
        url_existed_cond2 = self.db.session.query(VideoLocal).filter(VideoLocal.video_id == video_id).first() \
                                                                                                        is not None
        url_existed = url_existed_cond1 or url_existed_cond2
        if url_existed:
            logger.info("Video from %s existed!", url)
        return url_existed

    def is_video_id_exists(self, video_id: str):
        video_existed = self.db.session.query(VideoLocal).filter(VideoLocal.video_id == video_id).first() \
                                                                                                        is not None
        return video_existed

    def set_show_only_downloaded(self, show_downloaded_only):
        self.show_only_downloaded = show_downloaded_only
        self._update_model_data()

    def filter_by_category(self, category_name):
        self._category = category_name
        self._update_model_data()

    def add_videos_to_category(self, video_rows: list, category_name: str):
        for row in video_rows:
            video = self.video_data[row]
            category = self.db.session.query(Category).filter(Category.name == category_name).first()
            if category is None:
                category = Category(category)
            if category not in video.category:
                video.category.append(category)
        self.db.session.commit()
        self._update_model_data()
