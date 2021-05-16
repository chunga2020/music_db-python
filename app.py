import configparser
import mysql.connector
import sys

########################
# Function definitions #
########################

def album_exists(title, artist):
    """
    Return whether an album exists in the database.

    Parameters:
        title: title of the album to search for
        artist: artist of the album to search for

    Return True if found, False otherwise
    """
    album_check = conn.cursor()
    check_query = "SELECT * FROM albums "\
                  f"WHERE title = '{title}' AND artist = '{artist}'"
    if album_check.execute(check_query) is None:
        print(f"Album '{title} by {artist}' not found", file=sys.stderr)
        return False

    return True


def add_album(title, artist, genre, year, medium, type, complete,
        comment=None, composer=None):
    """
    Add an album to the database.

    The `comment` and `composer` fields default to None because they are not
    required in the database.

    Return True if the data is inserted successfully. Else, return False.
    """
    # make sure album doesn't already exist in database
    if album_exists(title, artist):
        print(f"Album '{title} by {artist}' already exists in database!",
            file=sys.stderr)
        return False

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
    # make sure album exists
    if not album_exists(title, artist):
        print(f"Album '{title} by {artist}' does not exist, so can't delete.",
            file=sys.stderr)
        return False
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

    valid_fields = [result[0] for result in results]
    print("Invalid field. Choose one of the following:", file=sys.stderr)
    for field in valid_fields:
        print(f"\t{field}", file=sys.stderr)
    return False

def __validate_enum(data, field):
    """
    Return whether data has the correct type for its SQL enum field.

    Parameters:
        data: the data to check
        field: the enum to check the data against

    Return True if the data is a valid value for the specified field, false
    otherwise.
    """
    cursor = conn.cursor()
    query = "SELECT column_type "\
            "FROM information_schema.columns "\
            f"WHERE table_schema = '{parser.get('mysql', 'database')}' "\
            "AND table_name = 'albums' "\
            f"AND column_name = '{field}'"
    cursor.execute(query)

    ################################################
    # decoding and parsing of messy SQL data types #
    ################################################

    # the list of tuples, as it comes back from SQL
    valid_options = cursor.fetchall()
    # drill down through list and tuple, giving us a bytes object
    valid_options = valid_options[0][0]
    # decode the bytes into a UTF-8 string
    valid_options = valid_options.decode()
    # skip "enum"
    valid_options = valid_options[4:]
    # get rid of the parens...
    valid_options = valid_options.strip('()')
    # and the single quotes...
    valid_options = valid_options.replace("'", "")
    # now we can make a list out of it
    valid_options = valid_options.split(",")

    # finally we can see if the data is valid or not
    if data in valid_options:
        return True
    else:
        print(f"Invalid choice for enum {field}. Choose one of the following",
                file=sys.stderr)
        for option in valid_options:
            print(f"\t{option}", file=sys.stderr)
        return False

def update_album(title, artist, field, data):
    """
    Update a field of an album.

    The title and artist fields are necessary because the database uses them
    together as the primary key of the `albums` table.

    Parameters:
        title: the title of the album to be updated
        artist: the artist of the album to be updated
        field: the field of the record to be udpated
        data: the new data for the field to be updated

    Return True on success; on error, return False and print an error.
    """
    # make sure album exists
    if not album_exists(title, artist):
        print(f"Album '{title} by {artist}' does not exist, so can't update.",
        file=sys.stderr)
        return False

    # make sure we got a valid field
    if not __validate_field(field):
        return False


    # if a year, make sure it fits MySQL's constraints on years
    if field == "year" and (int(data) < 1901 or int(data) > 2155):
        print("Year is not accepted by MySQL. Must be [1901, 2155].",
                file=sys.stderr)
        return False
    
    # Check varchar length constraints
    if len(data) > 100 and (field in ['title', 'artist', 'comment']):
        print(f"Data too long for field {field}. Reduce to <100 characters.",
            file=sys.stderr)
        return False
    if len(data) > 50 and (field in ['genre', 'composer']):
        print(f"Data too long for field {field}. Reduce to <50 characters.",
            file=sys.stderr)
        return False

    # Check enum validity
    if field in ['medium', 'type', 'complete']:
        if not __validate_enum(data, field):
            return False
    
    # We should be okay now, so do the update
    cursor = conn.cursor()
    query = f"UPDATE albums SET {field} = '{data}' "\
            f"WHERE title = '{title}' AND artist = '{artist}'"
    try:
        cursor.execute(query)
    except mysql.connector.Error as e:
        print(str(e), file=sys.stderr)
        return False
    conn.commit()
    return True


def handle_add_album():
    pass

def handle_delete_album():
    pass

def handle_update_album():
    pass

def handle_list_albums():
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

###################
# Create CLI loop #
###################
print("Welcome")
option = ""

while option != "q":
    print("Choose an option:")
    print("1. Add album")
    print("2. Delete album")
    print("3. Update album info")
    print("4. List albums")
    print("q. Quit")
    option = input("> ")

    if option == '1':
        handle_add_album()
    elif option == '2':
        handle_delete_album()
    elif option == '3':
        handle_update_album()
    elif option == '4':
        handle_list_albums()
    elif option == 'q':
        print("Goodbye!\n")
    else:
        pass


####################################
# Close the connection to clean up #
####################################
conn.close()