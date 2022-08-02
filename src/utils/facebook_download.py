#!/usr/bin/env python3
# Standard library imports
import os
import re
import html
import requests
import subprocess
import logging
import time
import random
from datetime import datetime
from pathlib import Path

# Third party imports
from urllib3.exceptions import MaxRetryError, NewConnectionError
from requests.exceptions import RequestException
from utils.slugify import slugify
from selenium.common.exceptions import NoSuchElementException, InvalidArgumentException, WebDriverException,ElementNotInteractableException
from selenium.webdriver.common.keys import Keys

# Local application imports
from config import Config
from utils.misc import remove_non_ascii, remove_html_tag, write_to_file, parse_fb_video_id, is_time_format, parse_video_quality, get_video_length
from utils.driver_manager import DriverManager

logger = logging.getLogger(__name__)

def get_video_pages_from_fb_page(page_url: str, download_all: bool = True):

    # result_urls = []

    fb_video_dict = {}

    try:
        with DriverManager() as driver_manager:
            driver = driver_manager.get()
            driver.get(page_url)

            html_element = driver.find_element_by_tag_name('html')
            if download_all:
                DELAY_BEFORE_PARSE_URLS = int(Config.getfloat_or_else("DOWNLOAD", "DELAY_SLOW", "60"))
            else:
                DELAY_BEFORE_PARSE_URLS = int(Config.getfloat_or_else("DOWNLOAD", "DELAY_FAST", "10"))
            for _ in range(DELAY_BEFORE_PARSE_URLS):
                html_element.send_keys(Keys.END)
                try:
                    element = driver.find_element_by_xpath("//a[@id='expanding_cta_close_button']")
                    element.click()
                except (NoSuchElementException, ElementNotInteractableException) as e:
                    pass
                try:
                    element = driver.find_element_by_xpath("//div[@aria-label='Đóng']")
                    element.click()
                except (NoSuchElementException, ElementNotInteractableException) as e:
                    pass
                # logger.debug("Sleep 1s...")
                time.sleep(1)

            elems_span = driver.find_elements_by_xpath("//span[@href]")
            elems_a = driver.find_elements_by_xpath("//a[@href]")
            elems = elems_span + elems_a



            for elem in elems:
                link = elem.get_attribute("href")
                try:
                    url = prepare_fb_video_url(link)
                except ValueError:
                    continue
                video_id = parse_fb_video_id(url)
                if video_id not in fb_video_dict:
                    fb_video_dict[video_id] = {}
                    fb_video_dict[video_id]['url'] = url
                    fb_video_dict[video_id]['text'] = []
                if elem.text == "":
                    continue
                if (is_time_format(elem.text)) and ('length' not in fb_video_dict[video_id]):
                    fb_video_dict[video_id]['length'] = elem.text
                if not is_time_format(elem.text):
                    fb_video_dict[video_id]['text'] =(elem.text)

    except (WebDriverException, MaxRetryError, NewConnectionError) as e:
        logger.error(e)

    logger.debug("get_video_urls_from_fb_page returned %d link", len(fb_video_dict))

    # return old to new result urls
    return fb_video_dict

def prepare_fb_video_url(link: str):
    fb_video_re1 = re.compile('/\d+/videos/\d+')
    fb_video_re2 = re.compile('https://(.+?)/(.+?)/videos/\d+')
    fb_video_re3 = re.compile('https://(.+?)/(.+?)/videos/(.+?)/\d+')

    if fb_video_re1.match(link):
        url = "https://www.facebook.com" + link.split('?')[0]
        return url
    elif fb_video_re2.match(link) or fb_video_re3.match(link):
        url = link.split('?')[0]
        return url
    else:
        raise ValueError(f"Incorrect link: {link}")

def parse_video_links(content):
    if 'x3CBaseURL' in content:
        video_matches = re.findall(r'FBQualityLabel=\\"([\w\d]+)\\">\\x3CBaseURL>(https://.+?)\\x3C',
                               content, re.DOTALL)
    else:
        content = content.replace("\\/", "/")
        video_matches = re.findall(r'FBQualityLabel=\\"([\w\d]+)\\">\\u003CBaseURL>(https://.+?)\\u003C',
                               content, re.DOTALL)
    video_matches = [(quality,html.unescape(link)) for (quality,link) in video_matches]
    logger.debug("%d video links found", len(video_matches))

    return video_matches

def parse_audio_links(content):
    if 'x3CBaseURL' in content:
        audio_matches = re.findall(r'CAudioChannelConfiguration.+?BaseURL>(https://.+?)\\x3C', content,
                               re.DOTALL)
    else: #u003C used
        content = content.replace("\\/", "/")
        audio_matches = re.findall(r'CAudioChannelConfiguration.+?BaseURL>(https://.+?)\\u003C', content,
                               re.DOTALL)
    audio_matches = [html.unescape(link) for link in audio_matches]
    logger.debug("audio_matches: %s", audio_matches)

    return audio_matches

def download_fb_video(url: str, download_livestream: bool = True):
    logger.info("Downloading video from " + url)

    try:
        with DriverManager() as driver_manager:
            driver = driver_manager.get()

            if "?" not in url:
                logger.debug("Open %s?__so__=channel_tab" % url)
                driver.get(url + "?__so__=channel_tab")
            else:
                logger.debug("Open %s" % url)
                driver.get(url)

            title = driver.find_element_by_xpath("//meta[@property='og:title']").get_attribute("content")
            logger.debug("video title: %s" % remove_non_ascii(title))
            description = " ".join(
                [x.text for x in driver.find_elements_by_xpath(r"//div[@data-testid='post_message']")])
            if description == "":
                description_elements = driver.find_elements_by_xpath("//meta[@name='twitter:description']")
                if len(description_elements)>0:
                    description = description_elements[0].get_attribute("content")
            logger.debug("video description: %s" % remove_non_ascii(description))
            page_source = driver.page_source
            if '"isLiveBroadcast":true' in page_source:
                is_live_stream = True
            else:
                is_live_stream = False

            DEBUG = Config.getboolean_or_else('MISC', 'DEBUG', False)
            if DEBUG:
                write_to_file(page_source, 'page.html')
    except (WebDriverException, MaxRetryError, NewConnectionError) as e:
        logger.error(e)
        return

    VIDEO_DIR = Path(Config.get_or_else('FOLDER', 'VIDEO_DIR', '../queue'))

    video = {}
    video['title'] = title
    video['description'] = description
    video['web_url'] = url
    video['downloaded'] = False
    video['video_id'] = parse_fb_video_id(url)

    if (not download_livestream) and is_live_stream:
        logger.info("%s is live stream link. Skipped!", url)
        return video

    video_matches = parse_video_links(page_source)
    video_matches = sorted(video_matches, key=lambda video_tuple: parse_video_quality(video_tuple[0]))
    audio_matches = parse_audio_links(page_source)

    # logger.debug("video_matches: %s", video_matches)
    # logger.debug("audio_matches: %s", audio_matches)

    try:
        quality, link_video = video_matches[-1]
        link_audio = audio_matches[-1]
    except IndexError:
        logger.warning("Cannot find video or audio link in %s. Skiped!" % url)
        return video

    # logger.debug("Link video: %s"%link_video)
    # logger.debug("Link audio: %s"%link_audio)

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S%f")
    video_path = VIDEO_DIR / f'{timestamp}_video.mp4'
    audio_path = VIDEO_DIR / f'{timestamp}_audio.mp4'
    merge_video_name = f'{slugify(title)[:100]}-{timestamp[:15]}.mp4'
    merge_video_path = VIDEO_DIR / merge_video_name

    logger.debug("Video path: %s"%video_path)
    logger.debug("Audio path: %s"%audio_path)
    logger.debug("Merge video path: %s"%merge_video_path)

    with requests.Session() as session:
        video_data = session.get(link_video, allow_redirects=True)
        audio_data = requests.get(link_audio, allow_redirects=True)
    try:
        with open(video_path, 'wb') as f:
            f.write(video_data.content)
        with open(audio_path, 'wb') as f:
            f.write(audio_data.content)
    except RequestException as e:
        logger.error(e)
        return

    logger.debug("Call ffmpeg to merg video and audio...")
    subprocess.call(
        ['ffmpeg', '-i', str(video_path), '-i', str(audio_path), '-map', '0:v', '-map', '1:a', '-c', 'copy',
         str(merge_video_path)],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    logger.debug("Video and audio merged!")

    #cleanup
    os.remove(video_path)
    os.remove(audio_path)

    video_length = get_video_length(merge_video_path)

    video['file_name'] = merge_video_name
    video['quality'] = quality
    video['downloaded'] = True
    video['video_length'] = int(video_length)

    logger.debug("Function download_fb_video stopped!")
    return video

if __name__ == "__main__":
    pass