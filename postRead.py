from bs4 import BeautifulSoup
import requests
import json
import time


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
        print("---------------------------------Comment Scrape for post (",
              id, ")", "---------------------------------")
        commentRead(id)


def countGet(id):
    print(id)
    link = "https://api.delfi.lv/comment/v1/graphql"
    payload = "{\"operationName\":\"cfe_getComments\",\"variables\":{\"articleId\":"+id + \
        ",\"modeType\":\"ANONYMOUS_MAIN\",\"orderBy\":\"DATE_ASC\",\"limit\":20,\"offset\":0,\"limitReplies\":3,\"orderByReplies\":\"DATE_DESC\"},\"query\":\"fragment CommentBody on Comment {\\n  id\\n  subject\\n  content\\n  created_time\\n  created_time_unix\\n  article_entity {\\n    article_id\\n    count_total\\n    count_anonymous\\n    __typename\\n  }\\n  vote {\\n    up\\n    down\\n    sum\\n    __typename\\n  }\\n  author {\\n    id\\n    customer_id\\n    idp_id\\n    __typename\\n  }\\n  parent_comment {\\n    id\\n    subject\\n    __typename\\n  }\\n  quote_to_comment {\\n    id\\n    subject\\n    __typename\\n  }\\n  reaction {\\n    comment_id\\n    name\\n    reaction\\n    count\\n    __typename\\n  }\\n  count_replies\\n  count_registered_replies\\n  status\\n  __typename\\n}\\n\\nquery cfe_getComments($articleId: Int!, $modeType: ModeType!, $offset: Int, $limit: Int, $orderBy: OrderBy, $limitReplies: Int, $orderByReplies: OrderBy, $lastCommentId: Int, $commentsBefore: Boolean) {\\n  getCommentsByArticleId(article_id: $articleId) {\\n    article_id\\n    count_total\\n    count_total_main_posts\\n    count_registered\\n    count_registered_main_posts\\n    count_anonymous_main_posts\\n    count_anonymous\\n    comments(mode_type: $modeType, offset: $offset, limit: $limit, orderBy: $orderBy) {\\n      ...CommentBody\\n      replies(lastCommentId: $lastCommentId, commentsBefore: $commentsBefore, limit: $limitReplies, orderBy: $orderByReplies) {\\n        ...CommentBody\\n        __typename\\n      }\\n      __typename\\n    }\\n    __typename\\n  }\\n}\\n\"}"
    header = {
        "Content-type": "application/json",
        "Origin": "https://www.delfi.lv/",
        "Cookie": "Some random cookie"
    }

    req = requests.post(link, headers=header, data=payload)
    res = json.loads(req.text)

    try:
        return res['data']['getCommentsByArticleId']['count_total']
    except:
        print("No comments found")
        return


def comments(offset, res):
    iter = 20
    for i in range(iter):
        print("\n", i, "\n")
        print("Time - ", res['data']['getCommentsByArticleId']
              ['comments'][i]['created_time'])
        print("Subject - ", res['data']
              ['getCommentsByArticleId']['comments'][i]['subject'])
        print("Content - ", res['data']
              ['getCommentsByArticleId']['comments'][i]['content'])
        print("Reply Count - ",
              res['data']['getCommentsByArticleId']['comments'][i]['count_replies'])
        print("Parent Comment - ",
              res['data']['getCommentsByArticleId']['comments'][i]['parent_comment'])
        print("Parent Comment - ",
              res['data']['getCommentsByArticleId']['comments'][i]['parent_comment'])

        try:
            print("Likes - ", res['data']['getCommentsByArticleId']
                  ['comments'][0]['reaction'][0]['count'])
        except:
            print("Likes - 0")

        try:
            print("Dislikes - ", res['data']['getCommentsByArticleId']
                  ['comments'][0]['reaction'][1]['count'])
        except:
            print("Dislikes - 0")

    return offset+iter


def commentRead(id):
    offset = 0
    count = countGet(id)
    while(offset != count):
        print(offset)
        time.sleep(2)

        link = "https://api.delfi.lv/comment/v1/graphql"
        payload = "{\"operationName\":\"cfe_getComments\",\"variables\":{\"articleId\":"+id + \
            ",\"modeType\":\"ANONYMOUS_MAIN\",\"orderBy\":\"DATE_ASC\",\"limit\":20,\"offset\":"+str(offset) + ",\"limitReplies\":3,\"orderByReplies\":\"DATE_DESC\"},\"query\":\"fragment CommentBody on Comment {\\n  id\\n  subject\\n  content\\n  created_time\\n  created_time_unix\\n  article_entity {\\n    article_id\\n    count_total\\n    count_anonymous\\n    __typename\\n  }\\n  vote {\\n    up\\n    down\\n    sum\\n    __typename\\n  }\\n  author {\\n    id\\n    customer_id\\n    idp_id\\n    __typename\\n  }\\n  parent_comment {\\n    id\\n    subject\\n    __typename\\n  }\\n  quote_to_comment {\\n    id\\n    subject\\n    __typename\\n  }\\n  reaction {\\n    comment_id\\n    name\\n    reaction\\n    count\\n    __typename\\n  }\\n  count_replies\\n  count_registered_replies\\n  status\\n  __typename\\n}\\n\\nquery cfe_getComments($articleId: Int!, $modeType: ModeType!, $offset: Int, $limit: Int, $orderBy: OrderBy, $limitReplies: Int, $orderByReplies: OrderBy, $lastCommentId: Int, $commentsBefore: Boolean) {\\n  getCommentsByArticleId(article_id: $articleId) {\\n    article_id\\n    count_total\\n    count_total_main_posts\\n    count_registered\\n    count_registered_main_posts\\n    count_anonymous_main_posts\\n    count_anonymous\\n    comments(mode_type: $modeType, offset: $offset, limit: $limit, orderBy: $orderBy) {\\n      ...CommentBody\\n      replies(lastCommentId: $lastCommentId, commentsBefore: $commentsBefore, limit: $limitReplies, orderBy: $orderByReplies) {\\n        ...CommentBody\\n        __typename\\n      }\\n      __typename\\n    }\\n    __typename\\n  }\\n}\\n\"}"
        header = {
            "Content-type": "application/json",
            "Origin": "https://www.delfi.lv/",
            "Cookie": "Some random cookie"
        }

        req = requests.post(link, headers=header, data=payload)
        res = json.loads(req.text)
        try:
            offset = comments(offset, res)
        except:
            print("Finished reading")
            return


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
