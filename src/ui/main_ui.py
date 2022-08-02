# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'main.ui'
#
# Created by: PyQt5 UI code generator 5.15.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1200, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1200, 26))
        self.menubar.setObjectName("menubar")
        self.menufrf = QtWidgets.QMenu(self.menubar)
        self.menufrf.setObjectName("menufrf")
        self.menuUpload = QtWidgets.QMenu(self.menubar)
        self.menuUpload.setObjectName("menuUpload")
        self.menuExit = QtWidgets.QMenu(self.menubar)
        self.menuExit.setObjectName("menuExit")
        self.menuView = QtWidgets.QMenu(self.menubar)
        self.menuView.setObjectName("menuView")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.action_download_video = QtWidgets.QAction(MainWindow)
        self.action_download_video.setObjectName("action_download_video")
        self.action_download_videos = QtWidgets.QAction(MainWindow)
        self.action_download_videos.setObjectName("action_download_videos")
        self.action_upload_to_fb = QtWidgets.QAction(MainWindow)
        self.action_upload_to_fb.setObjectName("action_upload_to_fb")
        self.action_stop_download = QtWidgets.QAction(MainWindow)
        self.action_stop_download.setEnabled(False)
        self.action_stop_download.setObjectName("action_stop_download")
        self.action_hide_failed_videos = QtWidgets.QAction(MainWindow)
        self.action_hide_failed_videos.setObjectName("action_hide_failed_videos")
        self.menufrf.addAction(self.action_download_video)
        self.menufrf.addAction(self.action_download_videos)
        self.menufrf.addAction(self.action_stop_download)
        self.menuUpload.addAction(self.action_upload_to_fb)
        self.menuView.addSeparator()
        self.menuView.addAction(self.action_hide_failed_videos)
        self.menubar.addAction(self.menufrf.menuAction())
        self.menubar.addAction(self.menuUpload.menuAction())
        self.menubar.addAction(self.menuView.menuAction())
        self.menubar.addAction(self.menuExit.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.menufrf.setTitle(_translate("MainWindow", "Download"))
        self.menuUpload.setTitle(_translate("MainWindow", "Upload"))
        self.menuExit.setTitle(_translate("MainWindow", "Exit"))
        self.menuView.setTitle(_translate("MainWindow", "View"))
        self.action_download_video.setText(_translate("MainWindow", "Single Video"))
        self.action_download_videos.setText(_translate("MainWindow", "Multiple Video"))
        self.action_upload_to_fb.setText(_translate("MainWindow", "To Facebook"))
        self.action_stop_download.setText(_translate("MainWindow", "Stop"))
        self.action_hide_failed_videos.setText(_translate("MainWindow", "Hide failed videos"))