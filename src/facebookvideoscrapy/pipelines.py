# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from queue import SimpleQueue
# from gettruyen.database.models import Chapters
# from gettruyen.database import truyenfulldb
# import logging

# n_item_bulk = 4000
#
# class GettruyenPipeline:
#
#     db = truyenfulldb.TruyenFullDatabase(dbname=r'truyenfull.db')
#     itemQueue = SimpleQueue()
#     adding = False
#
#     def process_item(self, item, spider):
#         self.itemQueue.put(item)
#         if self.itemQueue.qsize() > n_item_bulk and not self.adding:
#             self.adding = True
#             chapters = []
#             for chapter in [self.itemQueue.get() for i in range(n_item_bulk)]:
#                 t_chap = Chapters(name=chapter['name'], slug=chapter['slug'], url=chapter['url'],
#                                   content=chapter['content'])
#                 t_chap.book_id = chapter['book_id']
#                 chapters.append(t_chap)
#             logging.debug("Start add bulk chapters to database:")
#             # logging.debug(chapters)
#             try:
#                 self.db.session.bulk_save_objects(chapters)
#                 self.db.session.commit()
#             except Exception as e:
#                 self.db.session.rollback()
#             self.adding = False
#             logging.debug("Added bulk chapters to database.")
#         return item
#
#     def close_spider(self, spider):
#         chapters = []
#         while not self.itemQueue.empty():
#             chapter = self.itemQueue.get()
#             t_chap = Chapters(name=chapter['name'], slug=chapter['slug'], url=chapter['url'],
#                               content=chapter['content'])
#             t_chap.book_id = chapter['book_id']
#             chapters.append(t_chap)
#         logging.debug("Start add bulk remain chapters in queue to database before close:")
#         # logging.debug(chapters)
#         self.db.session.bulk_save_objects(chapters)
#         self.db.session.commit()
#         logging.debug("Added bulk chapters to database.")