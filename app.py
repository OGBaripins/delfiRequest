from log import get_logger
from postRead import flipPages
from postRead import commentRead
from bs4 import BeautifulSoup
import requests

logger = get_logger(__name__)

pages = 1


# readPost()

flipPages(pages)

# commentRead(str(53740237))
