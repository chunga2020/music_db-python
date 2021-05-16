import configparser
import mysql.connector

############################
# Configuring the app data #
############################

parser = configparser.ConfigParser()

parser.read("config.ini")

###############################
# Setting up MySQL connection #
###############################
conn = mysql.connector.connect(
        user=parser.get("mysql", "user"),
        password=parser.get("mysql", "password"),
        host=parser.get("mysql", "host"),
        database=parser.get("mysql", "database")
)
if conn is not None:
    print(conn)

####################################
# Close the connection to clean up #
####################################
conn.close()