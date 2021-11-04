import mysql.connector
from mysql.connector import errorcode

# phpMyAdmin is being used
try:
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password=""
    )
except:
    print("Connection to databse was unsuccessful")

cur = mydb.cursor()
tables = {}
databaseName = "delfi_request"


tables['post'] = (
    "CREATE TABLE `post` ("
    "  `link` VARCHAR(250) NOT NULL,"
    "  `title` VARCHAR(250),"
    "  `date` TIMESTAMP NOT NULL,"
    "  `fbShares` INT,"
    "  `photoName` VARCHAR (250),"
    "  `post_id` NUMERIC NOT NULL UNIQUE,"
    "  `author` VARCHAR (250),"
    "  PRIMARY KEY (`post_id`)"
    ") ENGINE=InnoDB")

tables['post_comment'] = (
    "CREATE TABLE `post_comment`("
    "   `post_id` NUMERIC NOT NULL UNIQUE,"
    "   `comment_id` NUMERIC NOT NULL UNIQUE,"
    "   `author` VARCHAR (250),"
    "   `date` TIMESTAMP,"
    "   `comment_body` VARCHAR (1000),"
    "   `upvote_count` NUMERIC,"
    "   `downvote_count` NUMERIC,"
    "   `parent_id` NUMERIC,"
    "  PRIMARY KEY (`comment_id`),"
    "  FOREIGN KEY (`post_id`) REFERENCES post(post_id)"
    ") ENGINE=InnoDB")

tables['config'] = (
    "CREATE TABLE `config`("
    "   `x` VARCHAR (10) NOT NULL,"
    "   `Z` VARCHAR (10) NOT NULL,"
    "   `Y` VARCHAR (10) NOT NULL"
    ") ENGINE=InnoDB")


tables['db_log'] = (
    "CREATE TABLE `db_log`("
    "   `procesName` VARCHAR (250) NOT NULL,"
    "   `status` VARCHAR (250) NOT NULL,"
    "   `start_time` TIMESTAMP,"
    "   `end_time` TIMESTAMP,"
    "   `comment` VARCHAR (5000)"
    ") ENGINE=InnoDB")


def createDb(cur):
    try:
        cur.execute(
            "CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8'".format(databaseName))
    except mysql.connector.Error as err:
        print("Failed creating database: {}".format(err))
        exit(1)


try:
    cur.execute("USE {}".format(databaseName))
except mysql.connector.Error as err:
    print("Database {} does not exists.".format(databaseName))
    if err.errno == errorcode.ER_BAD_DB_ERROR:
        createDb(cur)
        print("Database {} created successfully.".format(databaseName))
        mydb.database = databaseName
    else:
        print(err)
        exit(1)

for table_name in tables:
    table_description = tables[table_name]
    try:
        print("Creating table {}: ".format(table_name), end='')
        cur.execute(table_description)
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
            print("already exists.")
        else:
            print(err.msg)
    else:
        print("OK")

cur.close()
mydb.close()


# mycursor.execute("CREATE TABLE post (link (VARCHAR) NOT NULL), (title (VARCHAR)), (date(TIMESTAMP) NOT NULL), (fbShares(INT)), (photoName(VARCHAR)), (postID(NUMERIC) UNIQUE NOT NULL PRIMARY KEY), (author(VARCHAR))")
# mycursor.execute("CREATE TABLE post_comment (post_id(NUMERIC) FOREIGN KEY NOT NULL),(comment_id(NUMERIC)),(author(VARCHAR)), (date(TIMESTAMP)), (comment_body(NUMERIC)), (upvote_count(NUMERIC)), (downvote_count(NUMERIC)), (parent_id(NUMERIC))")
# mycursor.execute(
#     "CREATE TABLE config (x(VARCHAR) NOT NULL), (z(VARCHAR) NOT NULL), (y(VARCHAR) NOT NULL)")
# mycursor.execute("CREATE TABLE db_log (procesName(VARCHAR) NOT NULL), (status(VARCHAR) NOT NULL), (start_time(TIMESTAMP)), (end_time(TIMESTAMP)), (comment(VARCHAR 5000))")
