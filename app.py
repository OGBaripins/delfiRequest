from log import get_logger
from postRead import flipPages
from postRead import commentRead
from bs4 import BeautifulSoup
import requests

logger = get_logger(__name__)

pages = 2


# readPost()

flipPages(pages)

# commentRead(str(53731259))
