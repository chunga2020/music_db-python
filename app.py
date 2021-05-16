import configparser
import mysql.connector

############################
# Configuring the app data #
############################

parser = configparser.ConfigParser()

parser.read("config.ini")
for section in parser.sections():
    print(f"Reading data from section {section}")
    for key in parser[section]:
        print(f"\t{key} = {parser.get(section, key)}")