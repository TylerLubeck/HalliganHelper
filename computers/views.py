# Create your views here.
from django.shortcuts import render
from .models import Computer
from tas.models import Course, Request
from django.core.cache import cache

import logging

logger = logging.getLogger(__name__)


ROOMS_CACHE_KEY = "ROOMS_CACHE_KEY"
LABS_CACHE_KEY = "LABS_CACHE_KEY"


