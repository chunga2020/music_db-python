# music_db-python

## A simple music database interface

This application is a simple Python program that uses MySQL to help users track
their music library across different formats — physical and digital.

Dependencies:
* MySQL
* Python3
* See [requirements.txt](requirements.txt) for Python packages necessary to run
  this application.

## How to Run
1. Run `pip install -r requirements.txt` to install the packages needed by
   Python to run the application
2. Populate [config-sample.ini](config-sample.ini) with the values needed to
   access your MySQL database, and rename it to `config.ini` — `mv
   config-sample.ini config.ini`