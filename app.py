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
        print("add")
        # handle_add_album()
        print()
    elif option == '2':
        print("delete")
        # handle_delete_album()
        print()
    elif option == '3':
        print("update")
        # handle_update_album()
        print()
    elif option == '4':
        print("list")
        # handle_list_albums()
        print()
    elif option == 'q':
        print("Goodbye!\n")
    else:
        pass


####################################
# Close the connection to clean up #
####################################
conn.close()