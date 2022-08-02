import os
import base64
import requests
from requests_toolbelt import MultipartEncoder
import uuid
import logging

logger = logging.getLogger(__name__)


def download_file_to_tmp(source_url):
    """
    download `source_url` to /tmp return the full path, doing it in chunks so
    that we don't have to store everything in memory.
    """
    log.debug("download {0}".format(source_url))
    tmp_location = "/tmp/s3_downloads"

    # come up with a random name to avoid clashes.
    rand_name = str(uuid.uuid4().get_hex().lower()[0:6])

    local_filename = source_url.split('/')[-1]

    # get the extension if it has one
    if local_filename.count(".") > 0:
        ext = local_filename.split('.')[-1]
        tmp_filename = u"{0}.{1}".format(rand_name, ext)
    else:
        tmp_filename = u"{0}.mp4".format(local_filename)

    temp_media_location = os.path.join(tmp_location, tmp_filename)
    # make the temp directory
    if not os.path.exists(tmp_location):
        os.makedirs(tmp_location)

    r = requests.get(source_url, stream=True)
    log.debug("headers = {0}".format(r.headers))
    with open(temp_media_location, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:  # filter out keep-alive new chunks
                f.write(chunk)
                f.flush()
                os.fsync(f.fileno())
    log.debug("finished download to {0}".format(temp_media_location))
    return temp_media_location


def remove_file(temp_file):
    """ Given a valid file path remove it """
    if os.path.exists(temp_file):
        os.remove(temp_file)

def upload_file(video_url, page_id, access_token,
                description, title):
    """
    ``video_url``: this is where the video is in s3.
    ``page_id``:  me or a page_id for the page you want to post too.
    ``poster_url``:  the url to the poster (thumbnail) for this video
    ``access_token``: your facebook access token with permissions to upload
        to the page you want to post too.
    ``description``:  the description of the video you are posting.
    ``title``:  the title of the video you are posting
    """

    # download to data
    local_video_file = video_url
    video_file_name = local_video_file.split("/")[-1]

    if video_file_name and video_file_name.count(".") == 0:
        log.debug("video_file_name has no ext {0}".format(video_file_name))
        # if it doesn't have an extension add one to it.
        video_file_name = "{0}.mp4".format(video_file_name)
        log.debug("video_file_name converted to {0}".format(video_file_name))

    # need binary rep of this, not sure if this would do it

    # put it all together to post to facebook
    if page_id or page_id == 'me':
        path = 'me/videos'
    else:
        path = "{0}/videos".format(page_id)

    fb_url = "https://graph-video.facebook.com/{0}?access_token={1}".format(
             path, access_token)

    log.debug("video_file = {0}".format(local_video_file))
    log.debug("start upload to facebook")

    # multipart chunked uploads
    m = MultipartEncoder(
        fields={'description': description,
                'title': title,
                'source': (video_file_name, open(local_video_file, 'rb'))}
    )

    r = requests.post(fb_url, headers={'Content-Type': m.content_type}, data=m)

    if r.status_code == 200:
        j_res = r.json()
        facebook_video_id = j_res.get('id')
        log.debug("facebook_video_id = {0}".format(facebook_video_id))
    else:
        log.error("Facebook upload error: {0}".format(r.text))

    return facebook_video_id

def upload_file_with_thumb(video_url, page_id, poster_url, access_token,
                description, title):
    """
    ``video_url``: this is where the video is in s3.
    ``page_id``:  me or a page_id for the page you want to post too.
    ``poster_url``:  the url to the poster (thumbnail) for this video
    ``access_token``: your facebook access token with permissions to upload
        to the page you want to post too.
    ``description``:  the description of the video you are posting.
    ``title``:  the title of the video you are posting
    """

    # download to data
    local_video_file = video_url
    video_file_name = local_video_file.split("/")[-1]

    if video_file_name and video_file_name.count(".") == 0:
        log.debug("video_file_name has no ext {0}".format(video_file_name))
        # if it doesn't have an extension add one to it.
        video_file_name = "{0}.mp4".format(video_file_name)
        log.debug("video_file_name converted to {0}".format(video_file_name))

    # download to data
    local_poster_file = download_file_to_tmp(poster_url)

    # need to encode it.
    with open(local_poster_file, "rb") as image_file:
        poster_encoded_string = base64.b64encode(image_file.read())

    # need binary rep of this, not sure if this would do it

    # put it all together to post to facebook
    if page_id or page_id == 'me':
        path = 'me/videos'
    else:
        path = "{0}/videos".format(page_id)

    fb_url = "https://graph-video.facebook.com/{0}?access_token={1}".format(
             path, access_token)

    log.debug("video_file = {0}".format(local_video_file))
    log.debug("thumb_file = {0}".format(local_poster_file))
    log.debug("start upload to facebook")

    # multipart chunked uploads
    m = MultipartEncoder(
        fields={'description': description,
                'title': title,
                'thumb': poster_encoded_string,
                'source': (video_file_name, open(local_video_file, 'rb'))}
    )

    r = requests.post(fb_url, headers={'Content-Type': m.content_type}, data=m)

    if r.status_code == 200:
        j_res = r.json()
        facebook_video_id = j_res.get('id')
        log.debug("facebook_video_id = {0}".format(facebook_video_id))
    else:
        log.error("Facebook upload error: {0}".format(r.text))

    return facebook_video_id

if __name__ == "__main__":
    video_url = r"D:/01_PycharmProjects/DownloadFacebookVideo/videos/co-mot-ong-bo-sieu-nhan-nhung-khong-ngui-duoc-20201031.mp4"
    page_id = "1817904601806120"
    access_token = "EAAmnxzO4z1YBAAmv7grsRrzBVFUhxvJNrWoC4gZAUn2OBu42uhxYikU2UgpqpZAVnZCfiLjMDf51ne4ET2fO63OM37lKMN9atUtBag244JUfkvrVuwMrdpYXYSuaYHX21ZB9jN5MWMdP744P2petOYMv4Xz9oZCNikZBMlIXZC2IoE4jDVRxtTxJQAmBFgj63dRqzbxDMhtsBTXfiyzJnu1"
    description = "Có một ông bố siêu nhân nhưng không ngửi được #phimhay"
    title = "Có một ông bố siêu nhân nhưng không ngửi được"
    status = upload_file(video_url, page_id, access_token, description, title)
    print(status)