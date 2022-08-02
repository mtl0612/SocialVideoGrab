import os
import re
import time

from utils import pyperclip
from urllib.parse import urlparse, parse_qs

def remove_non_ascii(text: str) -> str:
    encoded_string = text.encode("ascii", "ignore")
    decode_string = encoded_string.decode()
    return decode_string

def remove_html_tag(content: str) -> str:
    from w3lib.html import remove_tags
    text_cleaned = remove_tags(content, keep = ("br",))
    text_cleaned = text_cleaned.replace("<br> ","\n")
    return text_cleaned

def addToClipBoard(text: str) -> None:
    pyperclip.copy(text)

def write_to_file(content: str, file_name: str = 'page.html'):
    with open(file_name, 'w', encoding='utf-8') as f:
        f.write(content)

def parse_fb_video_id(url: str):
    if re.match(r"https://(.+?)/(.+?)/videos/(.+?)", url):
       return url.split("?")[0].rstrip("/").split("/")[-1]

    if url.startswith("https://www.facebook.com/watch"):
        parsed_url = urlparse(url)
        parsed_queries = parse_qs(parsed_url.query)
        if 'v' in parsed_queries:
            return parsed_queries['v'][0]

    return ""

def validate_url(url: str):
    if url.startswith("https://www.facebook.com"):
        return True
    else:
        return False

def is_time_format(input: str):
    return is_ms_time_format(input) or is_hms_time_format(input)

def is_ms_time_format(input: str):
    try:
        time.strptime(input, '%M:%S')
        return True
    except ValueError:
        return False

def is_hms_time_format(input: str):
    try:
        time.strptime(input, '%H:%M:%S')
        return True
    except ValueError:
        return False

def parse_video_quality(quality: str):
    if re.fullmatch("\d+p", quality):
        return int(quality[:-1])
    else:
        return 0

def get_video_length(video_path):
    import subprocess
    result = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                             "format=duration", "-of",
                             "default=noprint_wrappers=1:nokey=1", video_path],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT)
    return float(result.stdout)

def video_length_repr(length_in_second: int):
    seconds = length_in_second % 60
    minutes = int(length_in_second / 60) % 60
    hours = int(length_in_second / 3600)

    return "%02d:%02d:%02d" % (hours, minutes, seconds)