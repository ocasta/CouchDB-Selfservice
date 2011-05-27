#/ -*- coding: utf-8 -*-
#
#
#   Author: Martin Higham
#
#   Copyright 2010 Ocastalabs Ltd.
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
#
import logging
import hashlib
import uuid
import couchdb

log = logging.getLogger('AuthUser')

class RegistrationError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

class Password:
    MIN_LENGTH = 5
    MAX_LENGTH = 12
    password = ""

    def __init__(self, password):
        if password:
            self.password = password

    def __str__(self):
        return self.password

    def isValid(self):
        if len(self.password)< self.MIN_LENGTH or len(self.password)> self.MAX_LENGTH:
            raise RegistrationError("Passwords must be between %s and %s characters in length" % (self.MIN_LENGTH, self.MAX_LENGTH))
        return True

    def encrypted(self):
        salt = uuid.uuid4()
        return salt, hashlib.sha1(self.password + salt.hex).hexdigest()

class AccountManager:
    couchServer = None
    config = None
    admin_url = None
    registrar_user = None
    MIN_NAME_LENGTH = 3

    def __init__(self, adminUser, adminPwd):
        self.adminUser = adminUser
        self.adminPwd = adminPwd
        self.admin_url = "http://" + self.adminUser+ ":" + adminPwd + "@localhost:5984/"
        self.couchServer = couchdb.Server(self.admin_url)


    # Create the CouchDB _user record
    # Used when user clicks register
    def create_account(self, name, password, template_db):
        name = name.lower()

        if len(name) < self.MIN_NAME_LENGTH:
            raise RegistrationError("Username must contain at least %s characters" % self.MIN_NAME_LENGTH)

        if name != name.encode("ascii", "ignore").translate(None,"&%+,./:;=?@ ?<>#%|\\[]{}~^`'"):
            raise RegistrationError("Invalid characters in username")

        pwd = Password(password)
        pwd.isValid()

        # Create the CouchDB user account.

        db = self.couchServer["_users"]
        salt, encrypted_pwd = pwd.encrypted()
        db.save({"_id":"org.couchdb.user:" + str(name),
                 "name": str(name),
                 "salt": salt.hex,
                 "password_sha" : encrypted_pwd,
                 "type":"user",
                 "roles":[] })

        publicDB_URL = self.admin_url + name
        # create the database by replicating from the template database
        # TODO: check if we need to do something else in Couch 1.1 to persist replication
        self.couchServer.replicate(source=self.admin_url+ template_db,
                                   target=publicDB_URL,
                                   create_target = True)

        log.debug("Database created")

        # set the security for the new database
        db = self.couchServer[name]
        db.resource.put_json("_security",
                                 body={"admins":{"names":[self.adminUser],"roles":[]},
                                       "readers":{"names":[name],"roles":[]}})

        log.debug("Database secured")
