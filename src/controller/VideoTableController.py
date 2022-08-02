from pathlib import Path
import os
import logging
from functools import partial

from PyQt5.QtCore import Qt, QSize, QSortFilterProxyModel
from PyQt5.QtWidgets import QWidget, QHeaderView, QErrorMessage, QMenu, QAction, QLineEdit, QMessageBox, QAbstractItemView
from PyQt5.QtGui import QCursor

from ui.video_table_widget_ui import Ui_VideoTableWidget
from models.VideoLocalQtModel import VideoLocalQtModel
from models.CategoryQtModel import CategoryQtModel
from models.common import Header
from config import Config

logger = logging.getLogger(__name__)


class VideoTableController(QWidget):
    def __init__(self, parent = None, model = None, category_model = None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if parent:
            self.parent = parent
        if model:
            self.table_model = model
        else:
            self.table_model = VideoLocalQtModel(parent = self)

        if category_model:
            self.category_model = category_model
        else:
            self.category_model = CategoryQtModel(parent = None)
        self.ui = Ui_VideoTableWidget()
        self.ui.setupUi(self)

        table_header = self.ui.tableView.horizontalHeader()


        self.proxy_model = QSortFilterProxyModel()
        self.proxy_model.setFilterKeyColumn(-1) # Search all columns.
        self.proxy_model.setFilterCaseSensitivity(False)
        self.proxy_model.setSourceModel(self.table_model)

        # self.proxy_model.sort(0, Qt.AscendingOrder)

        self.searchbar = QLineEdit()

        self.ui.verticalLayout.addWidget(self.searchbar)

        self.ui.tableView.setModel(self.proxy_model)
        self.ui.tableView.setSortingEnabled(True)
        self.ui.tableView.setContextMenuPolicy(Qt.CustomContextMenu)

        self.ui.tableView.setSelectionBehavior(QAbstractItemView.SelectRows)

        self.set_column_widths()
        self._connect_actions()

    def sizeHint(self) -> QSize:
        return QSize(500,600)

    def set_column_widths(self):
        for column_index, header in enumerate(self.table_model.headers):
            self.ui.tableView.setColumnWidth(column_index, header.width)

    def _connect_actions(self):
        # You can choose the type of search by connecting to a different slot here.
        # see https://doc.qt.io/qt-5/qsortfilterproxymodel.html#public-slots
        self.searchbar.textChanged.connect(self.proxy_model.setFilterFixedString)

        self.ui.tableView.customContextMenuRequested.connect(self.build_context_menu)
        self.ui.tableView.doubleClicked.connect(self.open_file_at)

    def build_context_menu(self, pos):
        proxy_indexes = self.ui.tableView.selectionModel().selectedIndexes()
        source_indexes = [self.proxy_model.mapToSource(index) for index in proxy_indexes]
        rows = [index.row() for index in source_indexes]
        rows = list(set(rows))
        if len(rows) == 0:
            return
        elif len(rows) == 1:
            # row = source_indexes[0].row()
            row = rows[0]
            context_menu = self.context_menu_for_single_item(row)
        else:
            # rows = [index.row() for index in source_indexes]
            context_menu = self.context_menu_for_multiple_item(rows)

        context_menu.popup(QCursor.pos())

    def context_menu_for_single_item(self, row):
        menu = QMenu(self)

        copyVideoPathAction = QAction('Copy Video path', self)
        copyVideoPathAction.triggered.connect(lambda: self.copy_video_path(row))
        menu.addAction(copyVideoPathAction)

        copyVideoDescriptionAction = QAction('Copy Video Description', self)
        copyVideoDescriptionAction.triggered.connect(lambda: self.copy_video_description(row))
        menu.addAction(copyVideoDescriptionAction)

        copyVideoSourceUrlAction = QAction('Copy Video Source URL', self)
        copyVideoSourceUrlAction.triggered.connect(lambda: self.copy_video_source_url(row))
        menu.addAction(copyVideoSourceUrlAction)

        menu.addSeparator()

        openWebUrlAction = QAction('Open web url...', self)
        openWebUrlAction.triggered.connect(lambda: self.open_url(row))
        menu.addAction(openWebUrlAction)

        openInExplorerAction = QAction('Open in Explorer...', self)
        openInExplorerAction.triggered.connect(lambda: self.open_in_explorer(row))
        menu.addAction(openInExplorerAction)

        menu.addSeparator()

        categoryMenu = self.populateCategoryMenu([row])
        menu.addMenu(categoryMenu)

        menu.addSeparator()

        removeVideoAction = QAction('Remove Video', self)
        removeVideoAction.triggered.connect(lambda: self.remove_videos([row]))
        menu.addAction(removeVideoAction)

        deleteRowAction = QAction('Delete', self)
        deleteRowAction.triggered.connect(lambda: self.delete_rows([row]))
        menu.addAction(deleteRowAction)

        return menu

    def context_menu_for_multiple_item(self,rows):

        menu = QMenu(self)

        categoryMenu = self.populateCategoryMenu(rows)
        menu.addMenu(categoryMenu)

        menu.addSeparator()
        
        removeVideoAction = QAction('Remove Video', self)
        removeVideoAction.triggered.connect(lambda: self.remove_videos(rows))
        menu.addAction(removeVideoAction)

        deleteRowsAction = QAction('Delete selected rows', self)
        deleteRowsAction.triggered.connect(lambda: self.delete_rows(rows))
        menu.addAction(deleteRowsAction)

        return menu

    def populateCategoryMenu(self, rows):
        menu =QMenu('Category', self)
        newAction = QAction('New', self)
        if self.parent:
            newAction.triggered.connect(self.parent.sig_new_category_input)
        menu.addAction(newAction)

        categories = self.category_model.get_all_categories()
        if len(categories) > 0 :
            menu.addSeparator()

        for category in categories:
            # logger.debug("category: %s", category)
            t_action = QAction(category, self)
            t_action.triggered.connect(partial(self.table_model.sig_add_videos_to_category.emit,rows, category))
            menu.addAction(t_action)
        return menu

    def hide_failed_videos(self, flag):
        self.table_model.showOnlyDownloadedVideosSignal.emit(flag)

    def remove_videos(self, rows):
        ret = QMessageBox.warning(self, '', "Are you sure you want to remove videos of selected rows?", \
                                   QMessageBox.Yes | QMessageBox.No)

        if ret == QMessageBox.Yes:
            self.table_model.removeVideosSignal.emit(rows)

    def delete_rows(self, rows):
        ret = QMessageBox.warning(self, '', "Are you sure you want to delete selected rows?", \
                                   QMessageBox.Yes | QMessageBox.No)

        if ret == QMessageBox.Yes:
            self.table_model.deleteRowsSignal.emit(rows)

    def copy_video_path(self, row):
        self.table_model.copyVideoPathSignal.emit(row)

    def copy_video_description(self, row):
        self.table_model.copyVideoDescriptionSignal.emit(row)

    def copy_video_source_url(self, row):
        self.table_model.copyVideoSourceUrlSignal.emit(row)

    def open_url(self, row):
        self.table_model.openWebUrlSignal.emit(row)

    def open_in_explorer(self, row):
        self.table_model.sig_open_in_explorer.emit(row)

    def open_file_at(self, index):
        source_index = self.proxy_model.mapToSource(index)
        row = source_index.row()

        # file_name = self.table_model.data()
        file_name = self.table_model.get_video_path(row)
        VIDEO_DIR = Path(Config.get_or_else('FOLDER', 'VIDEO_DIR', '../videos'))
        video_path = VIDEO_DIR / file_name
        # subprocess.run(['open', ], check=True)t
        try:
            os.startfile(video_path, 'open')
        except FileNotFoundError:
            error_dialog = QErrorMessage()
            error_dialog.showMessage(f'Cannot open file {video_path}')
            error_dialog.exec_()
        # print(video_path)

