# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'page_url_input_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.15.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_PageUrlInputDialog(object):
    def setupUi(self, PageUrlInputDialog):
        PageUrlInputDialog.setObjectName("PageUrlInputDialog")
        PageUrlInputDialog.resize(544, 149)
        self.verticalLayout = QtWidgets.QVBoxLayout(PageUrlInputDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(PageUrlInputDialog)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.comboBox = QtWidgets.QComboBox(PageUrlInputDialog)
        self.comboBox.setEditable(True)
        self.comboBox.setObjectName("comboBox")
        self.verticalLayout.addWidget(self.comboBox)
        self.checkDownloadAll = QtWidgets.QCheckBox(PageUrlInputDialog)
        self.checkDownloadAll.setObjectName("checkDownloadAll")
        self.verticalLayout.addWidget(self.checkDownloadAll)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.buttonBox = QtWidgets.QDialogButtonBox(PageUrlInputDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(PageUrlInputDialog)
        self.buttonBox.accepted.connect(PageUrlInputDialog.accept)
        self.buttonBox.rejected.connect(PageUrlInputDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(PageUrlInputDialog)

    def retranslateUi(self, PageUrlInputDialog):
        _translate = QtCore.QCoreApplication.translate
        PageUrlInputDialog.setWindowTitle(_translate("PageUrlInputDialog", "Download page videos"))
        self.label.setText(_translate("PageUrlInputDialog", "Input page url:"))
        self.checkDownloadAll.setText(_translate("PageUrlInputDialog", "Try to grab all video"))
