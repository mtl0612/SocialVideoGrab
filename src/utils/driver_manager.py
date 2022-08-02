import time
import logging
import functools
import subprocess

from selenium import webdriver
from selenium.webdriver.firefox.options import Options

from selenium.common.exceptions import WebDriverException
from urllib3.exceptions import MaxRetryError, NewConnectionError

from config import Config

logger = logging.getLogger(__name__)

# This code for hiding geckodrive cmd window
flag = 0x08000000  # No-Window flag
webdriver.common.service.subprocess.Popen = functools.partial(
    subprocess.Popen, creationflags=flag)

class DriverManager(object):
    driver = None
    last_run = None

    def __enter__(self):
        logger.debug("Entering the DriverManager context...")
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        logger.debug("Leaving the DriverManager context...")
        if self.driver:
            self.exit()
        # logger.debug(exc_type, exc_value, exc_tb, sep="\n")
        # if isinstance(exc_value, (WebDriverException, MaxRetryError, NewConnectionError)):
        if exc_value:
            logger.error(f"An exception occurred in DriverManager context: {exc_type}")
            logger.error(f"Exception message: {exc_value}")

    @classmethod
    def get(cls):
        # logger.info("cls.driver: %s", cls.driver)
        # logger.info("cls.last_run: %s", cls.last_run)
        MIN_DELAY = Config.getfloat_or_else('DOWNLOAD', 'MIN_DELAY', 60)
        if cls.last_run and (time_from_last_run := time.time() - cls.last_run) < MIN_DELAY:
            sleep_time = MIN_DELAY-time_from_last_run
            logger.debug("Time from last run is under %d. Sleep for %d seconds...", MIN_DELAY, sleep_time)
            time.sleep(sleep_time)
        if cls.driver is None:
            logger.debug("Initiate new driver...")
            options = Options()
            HEADLESS = Config.getboolean_or_else('DOWNLOAD', 'HEADLESS', True)
            options.headless = HEADLESS
            profile = webdriver.FirefoxProfile()
            profile.set_preference("app.update.auto", False)
            profile.set_preference("app.update.enabled", False)
            cls.driver = webdriver.Firefox(firefox_profile=profile, options=options)
        cls.last_run = time.time()
        return cls.driver

    @classmethod
    def close(cls):
        # return
        cls.driver.close()

    @classmethod
    def exit(cls):
        # return
        cls.driver.quit()
        cls.driver = None