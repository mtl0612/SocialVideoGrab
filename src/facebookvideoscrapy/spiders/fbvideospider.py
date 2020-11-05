# Standard library imports
import html
import logging
import os
import re
import subprocess
import time
from datetime import datetime
from pathlib import Path
import glob
import requests
from urllib.parse import urlparse
from urllib.parse import urljoin

# Third party imports
import scrapy
from scrapy_selenium import SeleniumRequest
from slugify import slugify

# Local application imports
from database import videodb
from database.models import VideoSource, VideoLocal
from functions import remove_html_tag

now = datetime.now()

timestr = time.strftime("%Y%m%d-%H%M%S")

log_dir = Path(os.environ['log_dir'])

link_log = logging.getLogger("link_log")
link_log_location = log_dir / f'{time.strftime("%Y%m%d-%H%M%S")}-link_log.log'
hdlr = logging.FileHandler(link_log_location, mode="a")
link_log.addHandler(hdlr)
link_log.setLevel(logging.INFO)
link_log.propagate = False

scrap_log = logging.getLogger("scrap_log")
scrap_log_location = log_dir / f'{time.strftime("%Y%m%d-%H%M%S")}-scrap_log.log'
scrap_hdlr = logging.FileHandler(scrap_log_location, mode="a", encoding='utf-8')
formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s', "%Y-%m-%d %H:%M:%S")
scrap_hdlr.setFormatter(formatter)
scrap_log.addHandler(scrap_hdlr)
scrap_log.setLevel(logging.DEBUG)
scrap_log.propagate = False


class FBVideoSpider(scrapy.Spider):
    name = "fbvideospider"
    db = videodb.FacebookVideoDatabase(dbname=r'facebookvideo.db')
    source_domain = "https://www.facebook.com"
    def __init__(self, *args, **kwargs):
        # turn off annoying logging, set LOG_LEVEL=DEBUG in settings.py to see more logs
        logger = logging.getLogger('scrapy.middleware')
        logger.setLevel(logging.WARNING)
        loggers = [logging.getLogger(name) for name in logging.root.manager.loggerDict]
        print(loggers)
        super().__init__(*args, **kwargs)

    def start_requests(self):
        scrap_log.debug("start_requests function started...")
        queue_dir = Path(os.environ['queue_dir'])
        for html_file_name in glob.glob(str(queue_dir / '*.htm*')):
            html_file_uri = ( queue_dir / html_file_name).as_uri()
            print(f'{html_file_uri}\n\n\n')
            yield scrapy.Request(url=html_file_uri, callback=self.parse_watch_page)

        # for video_source in self.db.session.query(VideoSource).all():
        #     # yield scrapy.Request(url=video_source.url, callback=self.parse_video_source, priority=0)
        #     # yield SplashRequest(video_source.url, self.parse_video_source, endpoint='render.json', args=splash_args)
        #     if 'watch' in video_source.url:
        #         yield SeleniumRequest(url=video_source.url, callback=self.parse_watch_page, wait_time=5)
        scrap_log.debug("start_requests function ended!")

    def parse_watch_page(self, response):
        response_url = response.url
        scrap_log.debug(f'Start parse watch page: {response_url}')
        link_log.info(f"VideoSource:{response_url}")
        page_source = str(response.body)
        video_link_matches = re.findall(r'(/[\d]+/videos/[\d]+/)', page_source, re.DOTALL)
        video_link_matches = [urljoin(self.source_domain, url) for url in video_link_matches]

        for link in video_link_matches:
            yield SeleniumRequest(url=link, callback=self.parse_video_page, wait_time=5,
                                  script='window.scrollTo(0, document.body.scrollHeight);')

    def parse_video_page(self, response):
        _url = response.url
        scrap_log.debug(f'Start parse video: {_url}')
        link_log.info(f"Video:{_url}")

        video_dir = Path(os.environ['video_dir'])
        page_source = str(response.body)
        title = response.xpath("//meta[@property='og:title']/@content").extract_first()
        if not title:
            title = response.xpath("//title/text()").extract_first()
        description = " ".join(response.xpath("//div[@data-testid='post_message']/node()").extract())
        description = remove_html_tag(description)

        video_matches = re.findall(r'FBQualityLabel=\\\\"([\w\d]+)\\\\">\\\\x3CBaseURL>(https://.+?)\\\\x3C',
                                   page_source, re.DOTALL)
        audio_matches = re.findall(r'CAudioChannelConfiguration.+?BaseURL>(https://.+?)\\\\x3C', page_source,
                                   re.DOTALL)
        quality, link_video = video_matches[-1]
        link_video = html.unescape(link_video)
        link_audio = html.unescape(audio_matches[-1])

        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S%f")
        video_path = video_dir / f'{timestamp}_video.mp4'
        audio_path = video_dir / f'{timestamp}_audio.mp4'
        merge_video_naem = f'{slugify(title)[:100]}-{timestamp[:8]}.mp4'
        merge_video_path = video_dir / merge_video_naem

        video_data = requests.get(link_video, allow_redirects=True)
        with open(video_path, 'wb') as f:
            f.write(video_data.content)

        audio_data = requests.get(link_audio, allow_redirects=True)
        with open(audio_path, 'wb') as f:
            f.write(audio_data.content)

        subprocess.call(
            ['ffmpeg', '-i', str(video_path), '-i', str(audio_path), '-map', '0:v', '-map', '1:a', '-c', 'copy',
             str(merge_video_path)],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        os.remove(video_path)
        os.remove(audio_path)


        video = VideoLocal()
        video.title = title
        video.description = description
        video.file_name = merge_video_naem
        video.web_url = _url

        self.db.session.add(video)
        self.db.session.commit()


    if __name__ == "__main__":
        pass
