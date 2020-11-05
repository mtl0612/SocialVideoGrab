#!/usr/bin/env python3

import locale
import re
import os
import sys

from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QPalette, QIcon, QColor
from PyQt5.QtWidgets import QApplication, QWidget, QStyleFactory


def main():
    from controller.MainController import MainController
    app = QApplication(sys.argv[0:1])
    main_window = MainController()
    main_window.show()
    app.exec_()

if __name__ == "__main__":
    main()

