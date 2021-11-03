from log import get_logger
from postRead import readPost
from postRead import flipPages
from bs4 import BeautifulSoup
import requests

logger = get_logger(__name__)

pages = 3


# readPost()

flipPages(pages)

# readComm()
