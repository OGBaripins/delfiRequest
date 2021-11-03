from bs4 import BeautifulSoup
import requests


def flipPages(pages):
    for page in range(1, pages + 1):
        print("------------------------------------------- ", page)
        readPost(page)


def readPost(page):

    html_text = requests.get(
        "https://www.delfi.lv/news/zinas/?page="+str(page)).text
    soup = BeautifulSoup(html_text, "lxml")

    posts = soup.find_all("div", class_="col-12 col-md-6 mb-4")
    posts = posts + soup.find_all("div", class_="col-6 mb-4")
    i = 0
    for post in posts:

        # Outside Post Scraping
        title = title_22(post) or title_16(post)
        link = post.find("a", href=True)
        link = str(link).split('href="')[1].split('"')[0]
        id = link.split("?id=")[1].strip()
        comments = commentGetter(post)
        photo = lazy_img(post) or disable_lazy_img(post)

        # In Post Scraping
        html_text = requests.get(link).text
        inPost = BeautifulSoup(html_text, "lxml")
        fbShares = facebookShares(inPost)
        author = author_media(inPost) or author_human(
            inPost) or multipleAuthor_human(inPost)

        # Final Print for post
        print("\nTitle - ", title, "\n Photo Link - ", photo, "\n Comment Count - ", comments, "\n Link - ",
              link, "\n ID - ", id, "\n Facebook Shares - ", fbShares, "\n Author/s - ", author, "\n")


def facebookShares(post):
    try:
        fbShares = post.find(
            "span", class_="facebook-share-count mvp-d-none").text.strip()
        return "("+fbShares+")"
    except:
        return "(0)"


def title_22(post):
    try:
        title = post.find(
            "h1", class_="text-size-22 text-size-md-19 mb-0 mt-2 headline__title").text.strip()

        if(title.startswith("PLUS")):
            title = title.split("PLUS").strip()
        return title
    except:
        return None


def title_16(post):
    try:
        title = post.find(
            "h1", class_="text-size-16 text-size-md-19 mb-0 mt-2 headline__title").text.strip()
        if(title.startswith("PLUS")):
            title = title.split("PLUS").strip()
        return title
    except:
        return None


def commentGetter(post):
    try:
        com = post.find(
            "a", class_="comment-count text-red-ribbon").text.strip()
        return com
    except:
        return "(0)"


def lazy_img(post):
    try:
        photo = post.find("img", class_="img-fluid w-100 lazy-img")
        newPhoto = imageDownload(photo)
        return newPhoto
    except:
        return None


def disable_lazy_img(post):
    try:
        photo = post.find(
            "img", class_="img-fluid w-100 lazy-img disable-lazy")
        newPhoto = imageDownload(photo)
        return newPhoto

    except:
        return None


def author_media(post):
    try:
        return post.find("h1", class_="text-size-3 mb-0 text-pale-sky").text.strip()
    except:
        return None


def author_human(post):
    try:
        return post.find("h1", class_="text-size-3 text-mine-shaft mb-0").text.strip()
    except:
        return None


def multipleAuthor_human(post):
    try:
        return post.find_all("h2", class_="text-size-3 text-mine-shaft mb-0").text.strip() or post.find("h2", class_="text-size-3 text-mine-shaft mb-0").text.strip()
    except:
        return None


def imageDownload(photo=""):
    try:
        photoLink = str(photo).split('src="')[1].split('" ')[0] or str(
            photo).split('data-src="')[1].split('" ')[0]
        photoName = photoLink.split("/")[-1]
        r = requests.get(photoLink)

        file = open("PostPhotos/"+photoName, "wb")
        file.write(r.content)
        file.close()

        return ("PostPhotos/"+photoName)
    except:
        return None
