import configparser
import mysql.connector
import sys

########################
# Function definitions #
########################

"""
Add an album to the database.

The `comment` and `composer` fields default to None because they are not
required in the database.

Return True if the data is inserted successfully. Else, return False.
"""
def add_album(title, artist, genre, year, medium, type, complete,
        comment=None, composer=None):
    cursor = conn.cursor()
    query = "INSERT INTO albums (title, artist, genre, year, comment,"\
            "composer, medium, type, complete) VALUES ("\
            f"'{title}', '{artist}', '{genre}', '{str(year)}', "
    if comment is not None:
        query += f"'{comment}', "
    else:
        query += "null, "
    if composer is not None:
        query += f"'{composer}', "
    else:
        query += "null, "
    if medium in ['cd', 'digital', 'vinyl']:
        query += f"'{medium}', "
    else:
        return False
    if type in ["studio album", "single", "ep"]:
        query += f"'{type}', "
    else:
        return False
    if complete in ['y', 'n']:
        query += f"'{complete}')"
    else:
        return False
    cursor.execute(query)
    conn.commit()
    return True

"""
List all albums.

Return True on success; on error, return False and print error.
"""
def list_albums():
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM albums", multi=True)
        for result in cursor.fetchall():
            print(result)
    except mysql.connector.Error as e:
        print(str(e), file=sys.stderr)
        return False
    return True

"""
Delete an album from the database.

This function only needs the title and artist of the album in question
because those two fields make up the primary key of the `albums` table

Return True on success; otherwise return False and print an error.
"""
def delete_album(title, artist):
    cursor = conn.cursor()
    query = f"DELETE FROM albums WHERE title = '{title}' AND "\
            f"artist = '{artist}'"     
    try:
        cursor.execute(query)
        conn.commmit()
    except mysql.connector.Error as e:
        print(str(e), file=sys.stderr)
        return False
    return True

############################
# Configuring the app data #
############################

parser = configparser.ConfigParser()

parser.read("config.ini")

###############################
# Setting up MySQL connection #
###############################
conn = None
try:
    conn = mysql.connector.connect(
            user=parser.get("mysql", "user"),
            password=parser.get("mysql", "password"),
            host=parser.get("mysql", "host"),
            database=parser.get("mysql", "database")
    )
except mysql.connector.Error as e:
    print(str(e), file=sys.stderr)
    exit(-1)

####################################
# Close the connection to clean up #
####################################
conn.close()