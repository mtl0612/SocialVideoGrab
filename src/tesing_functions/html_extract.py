# Local application imports
from database import videodb
from database.models import VideoSource, VideoLocal
from w3lib.html import remove_tags

def my_remove_html_tag(content):
    text_cleaned = remove_tags(content, keep = ("br",))
    text_cleaned = text_cleaned.replace("<br> ","\n")
    print(text_cleaned)

def update_videolocal_description():
    db = videodb.FacebookVideoDatabase(dbname=r'facebookvideo.db')
    for video in db.session.query(VideoLocal).all():
        video.description = my_remove_html_tag(video.description)
        db.session.commit()


update_videolocal_description()