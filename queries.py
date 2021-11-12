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
    sql_post = ("INSERT IGNORE INTO post (link, title, date, fb_shares, comment_count, photo_name, post_id, author)"
                    "VALUES (%s, %s ,%s, %s ,%s, %s, %s, %s)")
    try:
        cur.execute(sql_post, values)
        mydb.commit()
        cur.close()
        mydb.close()
    except mysql.connector.Error as err:
        print(err)
        


def _post_comment(values):
    mydb = con()
    cur = mydb.cursor()
    sql_post_comment = ("INSERT IGNORE INTO post_comment (post_id, comment_id, author, date, comment_subject, comment_body, reply_count, parent_id, upvote_count, downvote_count)"
                            "VALUES (%s, %s ,%s, %s ,%s, %s, %s, %s, %s, %s)")
    try:
        cur.executemany(sql_post_comment, values)
        mydb.commit()
        cur.close()
        mydb.close()
    except Exception as err:
        mydb.rollback()
        print(err)
        


def _config(values):
    mydb = con()
    cur = mydb.cursor()
    try:
        sql_config = ("INSERT IGNORE INTO config (identifier, value)"
                      "VALUES (%s, %s)")
        cur.execute(sql_config, values)
    except mysql.connector.Error as err:
        ("Duplicate entry, tryingto update table\n", err)
    mydb.commit()
    cur.close()
    mydb.close()

def _config_update (values):
    mydb = con()
    cur = mydb.cursor() 
    try:
        sql_config_update = ("UPDATE config SET value = %s WHERE identifier = %s")
        cur.execute(sql_config_update, tuple(reversed(values)))
        print("Tables were updated successfully")
    except mysql.connector.Error as err:
        print("Tables could not be updated\n",err)
    mydb.commit()
    cur.close()
    mydb.close()

def get_config():
    mydb = con()
    cur = mydb.cursor()
    try:
        sql_config_get = ("SELECT * FROM config")
        (cur.execute(sql_config_get))
        conf = cur.fetchall()
    except mysql.connector.Error as err:
        print("Tables could not be updated\n",err)
    cur.close()
    mydb.close()
    return conf
    


def _db_log(values):
    mydb = con()
    cur = mydb.cursor()
    try:
        sql_db_log = ("INSERT INTO db_log (process_name, status, start_time, end_time, comment)"
                      "VALUES(%s, %s, %s, %s, %s)")
        cur.execute(sql_db_log, values)
    except mysql.connector.Error as err:
        print(err)
    mydb.commit()
    cur.close()
    mydb.close()
