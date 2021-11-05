import mysql.connector
from mysql.connector import errorcode


def con():
    # phpMyAdmin is being used
    try:
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="delfi_request"
        )
    except:
        print("Connection to databse was unsuccessful")
    return mydb


def _post(values):
    mydb = con()
    cur = mydb.cursor()
    print("ye")
    try:
        sql_post = ("INSERT IGNORE INTO post (link, title, date, fb_shares, photo_name, post_id, author)"
                    "VALUES (%s, %s ,%s, %s ,%s, %s, %s)")
        print(cur.execute(sql_post, values))
        print(values)
    except mysql.connector.Error as err:
        print(err)
    print("done")
    cur.close()
    mydb.commit()
    mydb.close()


def _post_comment(values):
    mydb = con()
    cur = mydb.cursor()
    try:
        sql_post_comment = ("INSERT IGNORE INTO post_comment (post_id, comment_id, author, date, comment_subject, comment_body, reply_count, parent_id, upvote_count, downvote_count)"
                            "VALUES (%s, %s ,%s, %s ,%s, %s, %s, %s, %s, %s)")
        cur.execute(sql_post_comment, values)
    except mysql.connector.Error as err:
        print(err)
    cur.close()
    mydb.close()


def _config(values):
    mydb = con()
    cur = mydb.cursor()
    try:
        sql_config = ("INSERT INTO config (key, value)"
                      "VALUES(%s, %s)")
        cur.execute(sql_config, values)
    except mysql.connector.Error as err:
        print(err)
    cur.close()
    mydb.close()


def _db_log(values):
    mydb = con()
    cur = mydb.cursor()
    try:
        sql_db_log = ("INSERT INTO db_log (process_name, status, start_time, end_time, comment)"
                      "VALUES(%s, %s, %s, %s, %s)")
        cur.execute(sql_db_log, values)
    except mysql.connector.Error as err:
        print(err)
    cur.close()
    mydb.close()
