import requests
from bs4 import BeautifulSoup
from fastapi import FastAPI
import requests
from bs4 import BeautifulSoup
import uvicorn
# from pylogger import Logger
import logging
import shutil
import os
from pymongo.mongo_client import MongoClient

import pytest

from .split import make_batch
from .upload_gcp import upload_folder_to_gcs
