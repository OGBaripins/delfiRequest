from bs4 import BeautifulSoup
from queries import _post, _post_comment
import requests
import json
import time


def flipPages(pages):
    for page in range(1, pages + 1):
        print("------------------------------------------- ", page)
        time.sleep(0.5)
        readPost(page)


def readPost(page):
    print("jibat")
    html_text = requests.get(
        "https://www.delfi.lv/news/zinas/?page="+str(page)).text
    soup = BeautifulSoup(html_text, "lxml")

    posts = soup.find_all("div", class_="col-12 col-md-6 mb-4")
    posts = posts + soup.find_all("div", class_="col-6 mb-4")
    print("jibataaaaaaaaaaaa")
    i = 0
    print(posts)
    for post in posts:
        # Outside Post Scraping
        title = title_22(post) or title_16(post)
        link = post.find("a", href=True)
        link = str(link).split('href="')[1].split('"')[0]
        id = idGetter1(link) or idGetter2(link)
        comments = commentGetter(post)
        photo = lazy_img(post) or disable_lazy_img(post)

        # # In Post Scraping
        html_text = requests.get(link).text
        inPost = BeautifulSoup(html_text, "lxml")
        fbShares = facebookShares(inPost)
        author = author_media(inPost) or author_human(
            inPost) or multipleAuthor_human(inPost)
        date = dateConverter(inPost)

        # Final Print for post
        print("\nTitle - ", title, "\n Photo Link - ", photo, "\n Comment Count - ", comments,
              "\n Link - ", link, "\n ID - ", id, "\n Facebook Shares - ", fbShares, "\n Author/s - ", author)
        values = (link, title, date, int(fbShares), photo, int(id), author)
        _post(values)
        print("---------------------------------Comment Scrape for post (",
              id, ")", "---------------------------------")
        if(comments != "(0)"):
            commentRead(id)
        else:
            print("There are no comments to read!")
            print(
                "------------------------------------------------------------------------------------------")


def countGet(id):
    print(id)
    link = "https://api.delfi.lv/comment/v1/graphql"
    payload = "{\"operationName\":\"cfe_getComments\",\"variables\":{\"articleId\":"+id + \
        ",\"modeType\":\"ANONYMOUS_MAIN\",\"orderBy\":\"DATE_ASC\",\"limit\":100,\"offset\":0,\"limitReplies\":3,\"orderByReplies\":\"DATE_DESC\"},\"query\":\"fragment CommentBody on Comment {\\n  id\\n  subject\\n  content\\n  created_time\\n  created_time_unix\\n  article_entity {\\n    article_id\\n    count_total\\n    count_anonymous\\n    __typename\\n  }\\n  vote {\\n    up\\n    down\\n    sum\\n    __typename\\n  }\\n  author {\\n    id\\n    customer_id\\n    idp_id\\n    __typename\\n  }\\n  parent_comment {\\n    id\\n    subject\\n    __typename\\n  }\\n  quote_to_comment {\\n    id\\n    subject\\n    __typename\\n  }\\n  reaction {\\n    comment_id\\n    name\\n    reaction\\n    count\\n    __typename\\n  }\\n  count_replies\\n  count_registered_replies\\n  status\\n  __typename\\n}\\n\\nquery cfe_getComments($articleId: Int!, $modeType: ModeType!, $offset: Int, $limit: Int, $orderBy: OrderBy, $limitReplies: Int, $orderByReplies: OrderBy, $lastCommentId: Int, $commentsBefore: Boolean) {\\n  getCommentsByArticleId(article_id: $articleId) {\\n    article_id\\n    count_total\\n    count_total_main_posts\\n    count_registered\\n    count_registered_main_posts\\n    count_anonymous_main_posts\\n    count_anonymous\\n    comments(mode_type: $modeType, offset: $offset, limit: $limit, orderBy: $orderBy) {\\n      ...CommentBody\\n      replies(lastCommentId: $lastCommentId, commentsBefore: $commentsBefore, limit: $limitReplies, orderBy: $orderByReplies) {\\n        ...CommentBody\\n        __typename\\n      }\\n      __typename\\n    }\\n    __typename\\n  }\\n}\\n\"}"
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


def comments(offset, res, **done):
    iter = 100
    valuesStorage = []
    if(done):
        _post_comment(valuesStorage)
        return
    values = ()
    dict = {"Post ID": "id", "Author": "author", "Created Time - ": "created_time", "Comment Subject - ": "subject", "Comment Content - ": "content",
            "Reply Count - ": "count_replies", "Parent Comment - ": "parent_comment"}

    for i in range(iter):
        print("\n", "Article ID - ", res['data']
              ['getCommentsByArticleId']['article_id'])
        values = values+(res['data']['getCommentsByArticleId']['article_id'])
        for atribute in dict:
            print("\n", atribute,
                  res['data']['getCommentsByArticleId']['comments'][i][dict[atribute]])
            values = values+(res['data']['getCommentsByArticleId']
                             ['comments'][i][dict[atribute]])

        try:
            likes = (res['data']['getCommentsByArticleId']
                     ['comments'][0]['reaction'][0]['count'])
            print("Likes - ", likes)
            values = values+(likes)
        except:
            values = values+(0)
            print("Likes - 0")

        try:
            dislikes = (res['data']['getCommentsByArticleId']
                        ['comments'][0]['reaction'][1]['count'])
            print("Dislikes - ", dislikes)
            values = values+(dislikes)
        except:
            print("Dislikes - 0")
            values = values+(0)
        print(
            "------------------------------------------------------------------------------------------")
    valuesStorage.append(values)
    return offset+iter


def commentRead(id):
    offset = 0
    count = countGet(id)
    while(offset != count):
        time.sleep(1)

        link = "https://api.delfi.lv/comment/v1/graphql"
        payload = "{\"operationName\":\"cfe_getComments\",\"variables\":{\"articleId\":"+id + \
            ",\"modeType\":\"ANONYMOUS_MAIN\",\"orderBy\":\"DATE_ASC\",\"limit\":100,\"offset\":"+str(offset) + ",\"limitReplies\":3,\"orderByReplies\":\"DATE_DESC\"},\"query\":\"fragment CommentBody on Comment {\\n  id\\n  subject\\n  content\\n  created_time\\n  created_time_unix\\n  article_entity {\\n    article_id\\n    count_total\\n    count_anonymous\\n    __typename\\n  }\\n  vote {\\n    up\\n    down\\n    sum\\n    __typename\\n  }\\n  author {\\n    id\\n    customer_id\\n    idp_id\\n    __typename\\n  }\\n  parent_comment {\\n    id\\n    subject\\n    __typename\\n  }\\n  quote_to_comment {\\n    id\\n    subject\\n    __typename\\n  }\\n  reaction {\\n    comment_id\\n    name\\n    reaction\\n    count\\n    __typename\\n  }\\n  count_replies\\n  count_registered_replies\\n  status\\n  __typename\\n}\\n\\nquery cfe_getComments($articleId: Int!, $modeType: ModeType!, $offset: Int, $limit: Int, $orderBy: OrderBy, $limitReplies: Int, $orderByReplies: OrderBy, $lastCommentId: Int, $commentsBefore: Boolean) {\\n  getCommentsByArticleId(article_id: $articleId) {\\n    article_id\\n    count_total\\n    count_total_main_posts\\n    count_registered\\n    count_registered_main_posts\\n    count_anonymous_main_posts\\n    count_anonymous\\n    comments(mode_type: $modeType, offset: $offset, limit: $limit, orderBy: $orderBy) {\\n      ...CommentBody\\n      replies(lastCommentId: $lastCommentId, commentsBefore: $commentsBefore, limit: $limitReplies, orderBy: $orderByReplies) {\\n        ...CommentBody\\n        __typename\\n      }\\n      __typename\\n    }\\n    __typename\\n  }\\n}\\n\"}"
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
            print(
                "------------------------------------------------------------------------------------------")
            comments(None, None, True)
            return


def dateConverter(inPost):
    try:
        date = inPost.find(
            "time", class_="d-block text-pale-sky text-size-3 mb-2").text.strip()
        date = date.replace(".", "-")
        dateList = str(date).split("-")
        time = dateList[2].split(" ")
        dateList.append(time[0])
        dateList.append(time[1])
        dateList.remove(dateList[2])
        date = dateList[2]+"-" + dateList[1]+"-" + \
            dateList[0]+" " + dateList[3] + ":00"
    except:
        return None
    return date


def idGetter1(link):
    try:
        id = link.split("?id=")[1].strip()
        return id
    except:
        return None


def idGetter2(link):
    try:
        id = link.split("_")[0].split("/")[-1].strip()
        if(len(id) > 8):
            raise Exception("wrong id")
        return id
    except:
        return None


def facebookShares(post):
    try:
        fbShares = post.find(
            "span", class_="facebook-share-count mvp-d-none").text.strip()
        return fbShares
    except:
        return "0"


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
        return "0"


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
        print("Media")
        return post.find("h1", class_="text-size-3 mb-0 text-pale-sky").text.strip()
    except:
        return None


def author_human(post):
    try:
        print("Human")
        return post.find("h1", class_="text-size-3 text-mine-shaft mb-0").text.strip()
    except:
        return None


def multipleAuthor_human(post):
    try:
        print("More Huamns")
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
