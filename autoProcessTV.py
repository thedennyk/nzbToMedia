# Author: Nic Wolfe <nic@wolfeden.ca>
# URL: http://code.google.com/p/sickbeard/
#
# This file is part of Sick Beard.
#
# Sick Beard is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Sick Beard is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Sick Beard.  If not, see <http://www.gnu.org/licenses/>.


import sys
import urllib
import os.path
import ConfigParser

class AuthURLOpener(urllib.FancyURLopener):
    def __init__(self, user, pw):
        self.username = user
        self.password = pw
        self.numTries = 0
        urllib.FancyURLopener.__init__(self)
    
    def prompt_user_passwd(self, host, realm):
        if self.numTries == 0:
            self.numTries = 1
            return (self.username, self.password)
        else:
            return ('', '')

    def openit(self, url):
        self.numTries = 0
        return urllib.FancyURLopener.open(self, url)


def processEpisode(dirName, nzbName=None, failed=False):

    status = int(failed)
    config = ConfigParser.ConfigParser()
    configFilename = os.path.join(os.path.dirname(sys.argv[0]), "autoProcessTV.cfg")
    print "Loading config from", configFilename
    
    if not os.path.isfile(configFilename):
        print "ERROR: You need an autoProcessTV.cfg file - did you rename and edit the .sample?"
        sys.exit(-1)
    
    try:
        fp = open(configFilename, "r")
        config.readfp(fp)
        fp.close()
    except IOError, e:
        print "Could not read configuration file: ", str(e)
        sys.exit(1)
    
    watch_dir = ""
    host = config.get("SickBeard", "host")
    port = config.get("SickBeard", "port")
    username = config.get("SickBeard", "username")
    password = config.get("SickBeard", "password")
    try:
        ssl = int(config.get("SickBeard", "ssl"))
    except (ConfigParser.NoOptionError, ValueError):
        ssl = 0
    
    try:
        web_root = config.get("SickBeard", "web_root")
    except ConfigParser.NoOptionError:
        web_root = ""
    
    try:
        watch_dir = config.get("SickBeard", "watch_dir")
    except ConfigParser.NoOptionError:
        watch_dir = ""
        
    try:
        failed_fork = int(config.get("SickBeard", "failed_fork"))
    except (ConfigParser.NoOptionError, ValueError):
        failed_fork = 0
    
    #allows manual call of postprocess script if we have specified a watch_dir. Check that here.
    if nzbName = "Manual Run" and watch_dir == "":
        print "ERROR: In order to run this script manually you must specify a watch_dir in autoProcessTV.cfg"
        sys.exit(-1)
    #allows us to specify the default watch directory and call the postproecssing on another PC with different directory structure.
    if watch_dir != "":
        dirName = watch_dir
    
    params = {}
    
    params['quiet'] = 1

    # if you have specified you are using development branch from fork https://github.com/Tolstyak/Sick-Beard.git
    if failed_fork:
        params['dirName'] = dirName
        if nzbName != None:
            params['nzbName'] = nzbName
        params['failed'] = failed
        if status:
            print "The download failed. Sending 'failed' process request to SickBeard's failed branch"
        else:
            print "The download succeeded. Sending process request to SickBeard's failed branch"
                
    # this is our default behaviour to work with the standard Master branch of SickBeard
    else:
        params['dir'] = dirName
        if nzbName != None:
            params['nzbName'] = nzbName
        # the standard Master bamch of SickBeard cannot process failed downloads. So Exit here.
        if status:
            print "The download failed. Nothing to process"
            sys.exit()
        else:
            print "The download succeeded. Sending process request to SickBeard"

    myOpener = AuthURLOpener(username, password)
    
    if ssl:
        protocol = "https://"
    else:
        protocol = "http://"

    url = protocol + host + ":" + port + web_root + "/home/postprocess/processEpisode?" + urllib.urlencode(params)
    
    print "Opening URL:", url
    
    try:
        urlObj = myOpener.openit(url)
    except IOError, e:
        print "Unable to open URL: ", str(e)
        sys.exit(1)
    
    result = urlObj.readlines()
    for line in result:
        print line
        
