import logging
from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal

class Worker(QObject):
    finished = pyqtSignal()
    in_progress = pyqtSignal()

    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs

    @pyqtSlot()
    def run(self):
        # logging.debug("args: %s" % str(self.args))
        # logging.debug("kwargs: %s" % str(self.kwargs))
        self.fn(*self.args, **self.kwargs)
        self.finished.emit()