# -*- coding: utf-8 -*-
#
# Modified version of couchdb-solr2/lineprotocol.py
# Modified by Ocasta Labs 2011
#
# Original Copyright (c) 2008 Jacinto Ximénez de Guzmán
#
# Code licensed under the MIT License. See COPYING or
# http://www.opensource.org/licenses/mit-license.php
# for details.

import logging, sys
import json

log = logging.getLogger(__name__)

__all__ = ['LineProtocol']


class LineProtocol(object):

    def input(self):
        while True:
            try: line = sys.stdin.readline()
            except EOFError: break
            if not line: break
            try:
                obj = json.loads(line)
                yield obj
            except ValueError:
                log.exception("Problem serializing input: '%s'" % line)

    def outputJSON(self, code=200, data={}, headers={}):
        r = json.dumps({"code": ensure_json(code), "json": ensure_json(data), "headers": ensure_json(headers)})
        sys.stdout.write("%s\n" % r)
        log.debug('Sent JSON response "%s"' % r)
        sys.stdout.flush()

def ensure_json(thing):
    "'thing' is either JSON or a string of JSON.  Ensure it's JSON."
    if type(thing)==type(""): return json.loads(thing)
    else: return thing
