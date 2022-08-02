#!/usr/bin/env python3
# Standard library imports
import sys
import logging
from pathlib import Path

# Third party imports
from PyQt5.QtWidgets import QApplication

# Local application imports
from config import Config
from utils.debuggers import Debugger


logging.basicConfig(format="%(asctime)s - (%(name)s:%(lineno)s) - %(levelname)s: %(message)s",
                    level=logging.DEBUG)


selenium_logger = logging.getLogger('selenium.webdriver.remote.remote_connection')
selenium_logger.setLevel(logging.WARNING)
urllib3_logger = logging.getLogger('urllib3.connectionpool')
urllib3_logger.setLevel(logging.WARNING)


def main():
    logging.info("Program starting....")
    if (config_home := Path.home() / "FBVideoDownload/config.ini").is_file():
        logging.debug("config_home: %s", config_home)
        config_path = config_home
    elif (config_src := Path("./config.ini")).is_file():
        logging.debug("config_src: %s", config_src)
        config_path = config_src
    else:
        return

    logging.info("Loading config from %s...", config_path.resolve())
    Config.init_config(open(config_path))
    Debugger.enabled = True

    LOG_DIR = Path(Config.get_or_else("FOLDER", "LOG_DIR", "../logs"))
    log_path = LOG_DIR / "main.log"

    rootLogger = logging.getLogger("")
    logFormatter = logging.Formatter("[%(asctime)s] - (%(name)s:%(lineno)s) - %(levelname)s - %(message)s")
    consoleHandler = logging.FileHandler(log_path)
    consoleHandler.setFormatter(logFormatter)
    consoleHandler.setLevel("DEBUG")
    rootLogger.addHandler(consoleHandler)

    from controller.MainController import MainController
    app = QApplication(sys.argv[0:1])
    main_window = MainController()
    main_window.show()
    app.exec_()

if __name__ == "__main__":
    main()

