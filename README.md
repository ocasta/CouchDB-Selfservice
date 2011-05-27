CouchDB SelfService
====================================================

This is a simple CouchDB external process written in Python that processes the URL *http://localhost:5984/_register?username=xxx&passwd=YYY* or an POST to the same URL from a HTML form contain fields with the names username and password
It applies some simple validation to the username and password. It then creates a new CouchDB user in the standard _users database and creates the user a new database by replicating from a template database. Security is set on the new database so that it can be admin'ed by the admin and read only by the new user

Installation
-----------------------------------------------------

1. Ensure Python 2.x is installed and couchdb-python 0.8
2. Edit the file register.py and change the admin username and password to those of your couch database
3. Create a database called *template_db* that will be used as a template database for each user. If you call this database something else then edit the appropriate line in register.py
4. Create a directory and copy the three python files into it. 
5. Copy the selfservice.ini file into the directory <couchinstall>//etc/couchdb/local.d/
6. Edit the selfservice.ini file so that it correctly refers to your python executable and to the location of register.py
7. Restart CouchDB

You should now be able to create an account by running the command:
    *curl -v "http://localhost:5984/template_db/_register?username=firstuser&passwd=password"*
    
Don't forget that if you change anything in the python code you'll need to restart the CouchDB server for the change to take effect.

To Do
-------------------
There should be a simple example template database that contains a login form and Register button