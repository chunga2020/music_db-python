import configparser
import mysql.connector
import sys
from mysql.connector import cursor
import tabulate

###########################
# Useful global variables #
###########################
"""
Column names for `tabulate` table headers
"""
TABLE_HEADERS = ["Title", "Artist", "Genre", "Year", "Comment",
            "Composer", "Medium", "Type", "Complete"]

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
    album_check = conn.cursor(buffered=True)
    check_query = "SELECT * FROM albums "\
                  f"WHERE title = '{title}' AND artist = '{artist}'"
    album_check.execute(check_query)
    if album_check.fetchone() is None:
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

def get_albums(sort_fields=[]):
    """
    Get all albums for listing.

    Parameters:
        sort_fields: a list of the fields to sort the output by, in the order
        they are to be used. If empty, the default is to sort by title in
        ascending alphabetical order.

    Return the list of album tuples to be displayed; on error return None and
    print the error.
    """
    cursor = conn.cursor()
    try:
        query = "SELECT * FROM albums"
        if sort_fields != []:
            query += " ORDER BY "
            query += sort_fields.pop(0)
            while sort_fields != []:
                query += ", " + sort_fields.pop(0)
        cursor.execute(query, multi=True)
        return cursor.fetchall()
    except mysql.connector.Error as e:
        print(str(e), file=sys.stderr)
        return None

def __show_valid_fields():
    """ Display the columns of the `albums` table for the user's benefit """
    cursor = conn.cursor()
    query = "SELECT column_name "\
            "FROM information_schema.columns "\
            f"WHERE table_schema = '{parser.get('mysql', 'database')}' "\
            "AND table_name = 'albums'"
    cursor.execute(query)
    results = cursor.fetchall()
    fields = [result[0] for result in results]
    print("Valid fields:")
    for field in fields:
        print(f"* {field}")

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
    # make sure we got a valid field
    if not __validate_field(field):
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
    print("=== REQUIRED DATA ===".center(40))
    title = input("Enter album title (<= 100 characters): ")
    artist = input("Enter artist (<= 100 characters): ")
    genre = input("Enter genre (<= 50 characters): ")
    year = input("Enter album year (1901 through 2155 valid): ")
    medium = input("Enter medium (one of [cd, digital, vinyl]): ")
    type = input("Enter album type (one of [studio album, single, ep]: ")
    complete = input("Enter completeness status (y/n): ")

    print("=== OPTIONAL DATA ===".center(40))
    comment = input("Enter a comment (empty for none, <= 100 characters): ")
    if len(comment) == 0:
        comment = None
    composer = input("Enter a composer (empty for none, <= 50 characters): ")
    if len(composer) == 0:
        composer = None

    add_album(title, artist, genre, year, medium, type, complete,
            comment, composer)

def handle_delete_album():
    title = input("Title of album to delete: ")
    artist = input("Artist of album to delete: ")
    if album_exists(title, artist):
        delete_album(title, artist)
    else:
        print(f"Album '{title} by {artist}' does not exist, so can't delete.",
            file=sys.stderr)

def handle_update_album():
    title = input("Enter the title of the album to be updated: ")
    artist = input("Enter the artist of the album to be updated: ")

    # make sure album exists
    if not album_exists(title, artist):
        print(f"Album '{title} by {artist}' does not exist, so can't update.",
        file=sys.stderr)
        return
    __show_album(title, artist)
    field = input("Choose which field to update (all-lowercase): ")
    while not __validate_field(field):
        field = input("Choose which field to update (all-lowercase): ")

    new_data = input("Enter the new data for this field: ")

    # if a year, make sure it fits MySQL's constraints on years
    while field == "year" and (int(new_data) < 1901 or int(new_data) > 2155):
        print("Year is not accepted by MySQL. Must be [1901, 2155].",
                file=sys.stderr)
        new_data = input("Enter the new data for this field: ")

    # Check varchar length constraints
    while len(new_data) > 100 and (field in ['title', 'artist', 'comment']):
        print(f"Data too long for field {field}. Reduce to <100 characters. "
              f"Data was {len(new_data)} characters.",
              file=sys.stderr)
        new_data = input("Enter the new data for this field: ")

    while len(new_data) > 50 and (field in ['genre', 'composer']):
        print(f"Data too long for field {field}. Reduce to <50 characters. "
              f"Data was {len(new_data)} characters.",
              file=sys.stderr)
        new_data = input("Enter the new data for this field: ")

    # Check enum validity
    if field in ['medium', 'type', 'complete']:
        if not __validate_enum(new_data, field):
            return

    # if we get here, everything should be valid, so update the record
    update_album(title, artist, field, new_data)
    print("Here's the new record:".center(40))
    __show_album(title, artist)



def __show_album(title, artist):
    """
    Show the details for the specified album.

    Parameters:
        title: the title of the album to display
        artist: the artist of the album to display
    """
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM albums WHERE "\
                   f"title = '{title}' AND artist = '{artist}'")
    print(tabulate.tabulate([list(cursor.fetchone())], headers=TABLE_HEADERS))

def handle_find_album():
    title = input("Enter the title of the album to search for: ")
    artist = input("Enter the artist of the album to search for: ")

    if album_exists(title, artist):
        __show_album(title, artist)
    else:
        print(f"Album does not exist in database.", file=sys.stderr)

def handle_list_albums():
    print("Choose sort fields, in order to sort by, "\
            "separated by spaces (default: title)")
    __show_valid_fields()
    sort_fields = input("> ")
    sort_fields = sort_fields.split(" ")
    if sort_fields == ['']:
        sort_fields = []

    all_albums = get_albums(sort_fields)
    if all_albums is not None:
        print(tabulate.tabulate(all_albums,
            headers=["Title", "Artist", "Genre", "Year", "Comment",
                "Composer", "Medium", "Type", "Complete"]))

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
    print("5. Find album")
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
    elif option == '5':
        handle_find_album()
    elif option == 'q':
        print("Goodbye!\n")
    else:
        pass


####################################
# Close the connection to clean up #
####################################
conn.close()