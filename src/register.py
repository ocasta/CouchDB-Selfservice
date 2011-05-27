#/ -*- coding: utf-8 -*-
#
#   Author Martin Higham
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
#  This script should be configured as an external process within the CouchDB server
#  e.g.
#  [external]
#  register    /usr/bin/python /usr/local/etc/selfservice/register2.py
#
#  [httpd_db_handlers]
#  _register   {couch_httpd_external, handle_external_req, <<"register">>}
#
#
import traceback
import urlparse
from accountmanager import *
from lineprotocol import LineProtocol
import couchdb

log = logging.getLogger('Register')

def process_requests():
    # TODO: Change the admin user and password in the next line
    manager = AccountManager("admin", "password")

    protocol = LineProtocol()
    for req in protocol.input():
        if (req["headers"].has_key("Content-Type")
            and req["headers"]["Content-Type"].lower() == "application/x-www-form-urlencoded"):
            log.debug("Data received as application/x-www-form-urlencoded")
            formdata = urlparse.parse_qs(req["body"])
        else:
            log.debug("Data received as query string")
            formdata = req["query"]

        if not (formdata.has_key("username")) or formdata["username"] is None:
            log.info('Attempt to create account without an account name')
            protocol.outputJSON(code=400, data={"error":"Bad Request", "reason":"Username must be supplied"})
            continue
        elif not (formdata.has_key("passwd")) or formdata["passwd"] is None:
            log.info('Attempt to create account without a password')
            protocol.outputJSON(code=400, data={"error":"Bad Request", "reason":"Password must be supplied"})
            continue

        if (req["headers"].has_key("Content-Type")
            and req["headers"]["Content-Type"].lower() == "application/x-www-form-urlencoded"):
            username = formdata["username"][0]
            passwd = formdata["passwd"][0]
        else:
            username = formdata["username"]
            passwd = formdata["passwd"]

        try:
            # TODO: Change the name of the user database template in the next line
            manager.create_account(username, passwd, "template_db")
            protocol.outputJSON(code=201, data={"result" : "ok"})

        except RegistrationError, e:
            log.info("Validation error creating user %s. Reason %s", username, e)
            protocol.outputJSON(code=400, data={"error":"Registration Failure", "reason" : e.value})
            continue
        except couchdb.http.Unauthorized:
            log.error("Could not complete account creation for %s. Admin account not authorized successfully" % username)
            protocol.outputJSON(code=500, data={"error":"Server Error", "reason": "Server misconfigured" })
        except couchdb.http.ResourceConflict:
            log.error("Could not complete account creation for %s. User already exists" % username)
            protocol.outputJSON(code=400, data={"error":"Registration Failure", "reason": "Username in use" })

        #except Exception, e:
        #    log.error('Cannot create account: ' + username + " - " + str(e))
        #    protocol.outputJSON(code=500, data={"error":"Server Error", "reason": str(e) })

def main():
    # create log
    # Set up a specific log with our desired output leve

    log_format = '[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s'
    # TODO Change the log location here
    logging.basicConfig(filename="/var/log/selfservice.log",
                        level=logging.DEBUG,
                        format=log_format)

    log.info("Started")

    process_requests()

if __name__ == '__main__':
    try:
        main()
        log.info("Shutdown normally")
    except KeyboardInterrupt:
        log.info("Shutdown with Ctrl+C")
        raise # for error exit on command-line testing
    except Exception, e:
        log.debug(traceback.format_exc(5))
        log.info("register.py problem: Shutdown by exception: %r"%(e,))
        raise # for error exit on command-line testing
