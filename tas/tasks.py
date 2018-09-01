from __future__ import absolute_import
from celery import shared_task
import logging
import redis

logger = logging.getLogger(__name__)

POOL = redis.ConnectionPool(host='localhost', db=0)
