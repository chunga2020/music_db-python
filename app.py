import configparser
import mysql.connector
import sys

########################
# Function definitions #
########################

def add_album(title, artist, genre, year, medium, type, complete,
        comment=None, composer=None):
    """
    Add an album to the database.

    The `comment` and `composer` fields default to None because they are not
    required in the database.

    Return True if the data is inserted successfully. Else, return False.
    """
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

def get_albums():
    """
    Get all albums for listing.

    Return the list of album tuples to be displayed; on error return None and
    print the error.
    """
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM albums", multi=True)
        return cursor.fetchall()
    except mysql.connector.Error as e:
        print(str(e), file=sys.stderr)
        return None

def delete_album(title, artist):
    """
    Delete an album from the database.

    This function only needs the title and artist of the album in question
    because those two fields make up the primary key of the `albums` table

    Return True on success; otherwise return False and print an error.
    """
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


def __validate_field(field):
    """
    Return whether a field name is part of the SQL schema.

    In updating an album, the user needs a way to specify the field they want to
    update. Doing this introduces the possibility of errors if the user inputs
    an invalid field name, hence the need to check the input.

    Hinted to be private because users should not need to do this themselves

    Parameters:
        field: the field name to check
    """
    cursor = conn.cursor()
    # Get a tuple of all the column names
    query = "SELECT column_name "\
            "FROM information_schema.columns "\
            f"WHERE table_schema = '{parser.get('mysql', 'database')}' "\
            "AND table_name = 'albums'"
    cursor.execute(query)
    results = cursor.fetchall()
    for result in results:
        if field == result[0]:
            return True

    return False

def update_album():
    """
    Update a field of an album.

    The title and artist fields are necessary because the database uses them
    together as the primary key of the `albums` table.

    Parameters:
        title: the title of the album to be updated
        artist: the artist of the album to be updated
        field: the field of the record to be udpated
        data: the new data for the field to be updated
    """
    pass
        

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