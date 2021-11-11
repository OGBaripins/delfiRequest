from bs4 import BeautifulSoup
from queries import _post, _post_comment, _config, _db_log
import sys
import requests
import json
import time

conf = {
        "postInterval": ("post_read_interval_sec", "11"), 
        "commentReadInterval": ("comment_read_interval_sec", "11"), 
        "postPageLimit": ("post_page_count_limit", "21"), 
        "commentCount": ("comments_one_request_count", "20")
    }

def setUp():
    global conf
    for i in conf:
        _config(conf[i])
    return conf


def flipPages(pages):
    for page in range(1, pages + 1):
        print("------------------------------------------- ", page)
        time.sleep(1)
        readPost(page)


def readPost(page):
    html_text = requests.get("https://www.delfi.lv/news/zinas/?page="+str(page)).text
    soup = BeautifulSoup(html_text, "lxml")

    posts = soup.find_all("div", class_="col-12 col-md-6 mb-4")
    posts = posts + soup.find_all("div", class_="col-6 mb-4")
    
    for post in posts:
        time.sleep(1)
        # Outside Post Scraping
        title = title_22(post) or title_16(post)
        link = post.find("a", href=True)
        link = str(link).split('href="')[1].split('"')[0]
        comID = idGetter1(link) or idGetter2(link)
        comments = commentGetter(post)
        photo = lazy_img(post) or disable_lazy_img(post)

        # # In Post Scraping
        html_text = requests.get(link).text
        inPost = BeautifulSoup(html_text, "lxml")

        fbShares = facebookShares(inPost)
        author = author_media(inPost) or author_human(inPost) or multipleAuthor_human(inPost)
        date = dateConverter(inPost)

        # Final Print for post
        print("\nTitle - ", title, "\n Photo Link - ", photo, "\n Comment Count - ", comments,
              "\n Link - ", link, "\n ID - ", comID, "\n Facebook Shares - ", fbShares, "\n Author/s - ", author)
        values = (link, title, date, int(fbShares), int(comments), photo, int(comID), author)
        _post(values)
        print("---------------------------------Comment Scrape for post (",comID, ")", "---------------------------------")
        if(comments != "0"):
            commentRead(comID)
        else:
            print("There are no comments to read!")
            print("------------------------------------------------------------------------------------------")


def countGet(comID):
    print(comID)
    link = "https://api.delfi.lv/comment/v1/graphql"
    payload = "{\"operationName\":\"cfe_getComments\",\"variables\":{\"articleId\":"+comID + \
        ",\"modeType\":\"ANONYMOUS_MAIN\",\"orderBy\":\"DATE_ASC\",\"limit\":20,\"offset\":0,\"limitReplies\":3,\"orderByReplies\":\"DATE_DESC\"},\"query\":\"fragment CommentBody on Comment {\\n  id\\n  subject\\n  content\\n  created_time\\n  created_time_unix\\n  article_entity {\\n    article_id\\n    count_total\\n    count_anonymous\\n    __typename\\n  }\\n  vote {\\n    up\\n    down\\n    sum\\n    __typename\\n  }\\n  author {\\n    id\\n    customer_id\\n    idp_id\\n    __typename\\n  }\\n  parent_comment {\\n    id\\n    subject\\n    __typename\\n  }\\n  quote_to_comment {\\n    id\\n    subject\\n    __typename\\n  }\\n  reaction {\\n    comment_id\\n    name\\n    reaction\\n    count\\n    __typename\\n  }\\n  count_replies\\n  count_registered_replies\\n  status\\n  __typename\\n}\\n\\nquery cfe_getComments($articleId: Int!, $modeType: ModeType!, $offset: Int, $limit: Int, $orderBy: OrderBy, $limitReplies: Int, $orderByReplies: OrderBy, $lastCommentId: Int, $commentsBefore: Boolean) {\\n  getCommentsByArticleId(article_id: $articleId) {\\n    article_id\\n    count_total\\n    count_total_main_posts\\n    count_registered\\n    count_registered_main_posts\\n    count_anonymous_main_posts\\n    count_anonymous\\n    comments(mode_type: $modeType, offset: $offset, limit: $limit, orderBy: $orderBy) {\\n      ...CommentBody\\n      replies(lastCommentId: $lastCommentId, commentsBefore: $commentsBefore, limit: $limitReplies, orderBy: $orderByReplies) {\\n        ...CommentBody\\n        __typename\\n      }\\n      __typename\\n    }\\n    __typename\\n  }\\n}\\n\"}"
    header = {
        "Content-type": "application/json",
        "Origin": "https://www.delfi.lv/",
        "Cookie": "Some random cookie"
    }

    req = requests.post(link, headers=header, data=payload)
    res = json.loads(req.text)

    try:
        print("Total comment count - ",res['data']['getCommentsByArticleId']['count_anonymous'])
        return res['data']['getCommentsByArticleId']['count_anonymous']
    except Exception as e:
        print(e)
        print("No comments found")
        return


def comments(offset, res):
    allValues = ()
    i = 20
    types = {"Post ID": "id", "Author": "author", "Created Time - ": "created_time", "Comment Subject - ": "subject", "Comment Content - ": "content",
            "Reply Count - ": "count_replies", "Parent Comment - ": "parent_comment"}
    try:
        for com in range(i):
            articleID  = res['data']['getCommentsByArticleId']['article_id']
            print("\n", "Article ID - ", articleID)
            values = ()
            values = values + (articleID,)
            for atribute in types:
                print("\n", atribute,(res['data']['getCommentsByArticleId']['comments'][com][types[atribute]]))
                values = values+(str(res['data']['getCommentsByArticleId']['comments'][com][types[atribute]]),)

            try:
                likes = (res['data']['getCommentsByArticleId']['comments'][0]['reaction'][0]['count'])
                print("Likes - ", likes)
                values = values+(likes, )
            except:
                likes= "0"
                values = values+(likes, )
                print("Likes - 0")

            try:
                dislikes = (res['data']['getCommentsByArticleId']['comments'][0]['reaction'][1]['count'])
                print("Dislikes - ", dislikes)
                values = values+(dislikes, )
            except:
                dislikes = "0"
                values = values+(dislikes, )
                print("Dislikes - 0")
            print("------------------------------------------------------------------------------------------")
            print(values)
            allValues = allValues +(values, )
            values = ()
    except IndexError as e:
        print("-------------  ",e)
        print(allValues)
        _post_comment(allValues)
    except Exception as e:
        print("nicht gut\n",e)
    return offset+i

def commentRead(comID):
    startTime = getTime()
    offset = 0
    count = countGet(comID)
    while(offset < count):
        time.sleep(1)
        
        link = "https://api.delfi.lv/comment/v1/graphql"
        payload = "{\"operationName\":\"cfe_getComments\",\"variables\":{\"articleId\":"+comID + \
            ",\"modeType\":\"ANONYMOUS_MAIN\",\"orderBy\":\"DATE_ASC\",\"limit\":20,\"offset\":"+str(offset) + ",\"limitReplies\":3,\"orderByReplies\":\"DATE_DESC\"},\"query\":\"fragment CommentBody on Comment {\\n  id\\n  subject\\n  content\\n  created_time\\n  created_time_unix\\n  article_entity {\\n    article_id\\n    count_total\\n    count_anonymous\\n    __typename\\n  }\\n  vote {\\n    up\\n    down\\n    sum\\n    __typename\\n  }\\n  author {\\n    id\\n    customer_id\\n    idp_id\\n    __typename\\n  }\\n  parent_comment {\\n    id\\n    subject\\n    __typename\\n  }\\n  quote_to_comment {\\n    id\\n    subject\\n    __typename\\n  }\\n  reaction {\\n    comment_id\\n    name\\n    reaction\\n    count\\n    __typename\\n  }\\n  count_replies\\n  count_registered_replies\\n  status\\n  __typename\\n}\\n\\nquery cfe_getComments($articleId: Int!, $modeType: ModeType!, $offset: Int, $limit: Int, $orderBy: OrderBy, $limitReplies: Int, $orderByReplies: OrderBy, $lastCommentId: Int, $commentsBefore: Boolean) {\\n  getCommentsByArticleId(article_id: $articleId) {\\n    article_id\\n    count_total\\n    count_total_main_posts\\n    count_registered\\n    count_registered_main_posts\\n    count_anonymous_main_posts\\n    count_anonymous\\n    comments(mode_type: $modeType, offset: $offset, limit: $limit, orderBy: $orderBy) {\\n      ...CommentBody\\n      replies(lastCommentId: $lastCommentId, commentsBefore: $commentsBefore, limit: $limitReplies, orderBy: $orderByReplies) {\\n        ...CommentBody\\n        __typename\\n      }\\n      __typename\\n    }\\n    __typename\\n  }\\n}\\n\"}"
        header = {
            "Content-type": "application/json",
            "Origin": "https://www.delfi.lv/",
            "Cookie": "Some random cookie"
        }
        
        req = requests.post(link, headers=header, data=payload)
        res = json.loads(req.text)
        offset = comments(offset, res)
    else:
        _db_log((sys._getframe().f_code.co_name, "INFO", startTime, getTime(), "Comments have been successfully read"))
        print( "------------------------------------------------------------------------------------------")
        print("Finished reading")
        print( "------------------------------------------------------------------------------------------")
        return


def dateConverter(inPost):
    startTime = getTime()
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
        _db_log((sys._getframe().f_code.co_name, "INFO", startTime, getTime(), "Post Date was fetched and converted successfully"))
    except:
        _db_log((sys._getframe().f_code.co_name, "INFO", startTime, getTime(), "Post Date could not be fetched or converted"))
        return None
    return date


def idGetter1(link):
    startTime = getTime()
    try:
        comID = link.split("?id=")[1].strip()
        _db_log((sys._getframe().f_code.co_name, "INFO", startTime, getTime(), "Post ID was fetched successfully"))
        return comID
    except:
        _db_log((sys._getframe().f_code.co_name, "WARNING", startTime, getTime(), "An exception occured while fetching Post ID or The second ID function will be called"))
        return None


def idGetter2(link):
    startTime = getTime()
    try:
        comID = link.split("_")[0].split("/")[-1].strip()
        _db_log((sys._getframe().f_code.co_name, "INFO", startTime, getTime(), "Post ID was fetched successfully"))
        if(len(comID) > 8):
            raise Exception("wrong id")
        return comID
    except:
        _db_log((sys._getframe().f_code.co_name, "WARNING", startTime, getTime(), "An exception occured while fetching Post ID or The second ID function will be called"))
        return None


def facebookShares(post):
    startTime = getTime()
    try:
        fbShares = post.find("span", class_="facebook-share-count mvp-d-none").text.strip()
        return fbShares
    except:
        return "0"


def title_22(post):
    startTime = getTime()
    try:
        title = post.find(
            "h1", class_="text-size-22 text-size-md-19 mb-0 mt-2 headline__title").text.strip()

        if(title.startswith("PLUS")):
            title = title.split("PLUS").strip()
        return title
    except:
        return None


def title_16(post):
    startTime = getTime()
    try:
        title = post.find(
            "h1", class_="text-size-16 text-size-md-19 mb-0 mt-2 headline__title").text.strip()
        if(title.startswith("PLUS")):
            title = title.split("PLUS").strip()
        return title
    except:
        return None


def commentGetter(post):
    startTime = getTime()
    try:
        com = post.find(
            "a", class_="comment-count text-red-ribbon").text.strip()
        com = com.split("(")[1].split(")")[0].strip()
        return com
    except:
        return "0"


def lazy_img(post):
    startTime = getTime()
    try:
        photo = post.find("img", class_="img-fluid w-100 lazy-img")
        newPhoto = imageDownload(photo)
        return newPhoto
    except:
        return None


def disable_lazy_img(post):
    startTime = getTime()
    try:
        photo = post.find(
            "img", class_="img-fluid w-100 lazy-img disable-lazy")
        newPhoto = imageDownload(photo)
        return newPhoto

    except:
        return None


def author_media(post):
    startTime = getTime()
    try:
        print("Media")
        return post.find("h1", class_="text-size-3 mb-0 text-pale-sky").text.strip()
    except:
        return None


def author_human(post):
    startTime = getTime()
    try:
        print("Human")
        return post.find("h1", class_="text-size-3 text-mine-shaft mb-0").text.strip()
    except:
        return None


def multipleAuthor_human(post):
    startTime = getTime()
    try:
        print("More Huamns")
        return post.find_all("h2", class_="text-size-3 text-mine-shaft mb-0").text.strip() or post.find("h2", class_="text-size-3 text-mine-shaft mb-0").text.strip()
    except:
        return None


def imageDownload(photo=""):
    startTime = getTime()
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
    

def getTime():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

