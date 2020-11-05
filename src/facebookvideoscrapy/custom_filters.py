from scrapy.dupefilters import RFPDupeFilter
from database import videodb
from database.models import VideoLocal
import logging

class SeenURLFilter(RFPDupeFilter):
    """A dupe filter that considers the URL"""

    def __init__(self, *args, **kwargs):
        db = videodb.FacebookVideoDatabase(dbname=r'facebookvideo.db')
        self.urls_seen = [x[0] for x in db.session.query(VideoLocal.web_url).all()]
        # logging.debug(f"There are {len(self.urls_seen)} urls in urls_seen")
        RFPDupeFilter.__init__(self, *args, **kwargs)

    def request_seen(self, request):
        if request.url in self.urls_seen:
            # logging.debug(f"SeenURLFilter - Request.url {request.url} found in urls_seen list")
            return True
        return super(SeenURLFilter, self).request_seen(request)