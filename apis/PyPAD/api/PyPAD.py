#!/usr/bin/python

# PyPAD.py
#
# PAD processor for Rivendell
#
#   (C) Copyright 2018 Fred Gleason <fredg@paravelsystems.com>
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License version 2 as
#   published by the Free Software Foundation.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public
#   License along with this program; if not, write to the Free Software
#   Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
#

import datetime
import socket
import json

#
# Enumerated Constants (sort of)
#
# Escape types
#
ESCAPE_NONE=0
ESCAPE_XML=1
ESCAPE_URL=2
ESCAPE_JSON=3

#
# PAD Types
#
TYPE_NOW='now'
TYPE_NEXT='next'

#
# Field Names
#
FIELD_START_DATETIME='startDateTime'
FIELD_CART_NUMBER='cartNumber'
FIELD_CART_TYPE='cartType'
FIELD_LENGTH='length'
FIELD_YEAR='year'
FIELD_GROUP_NAME='groupName'
FIELD_TITLE='title'
FIELD_ARTIST='artist'
FIELD_PUBLISHER='publisher'
FIELD_COMPOSER='composer'
FIELD_ALBUM='album'
FIELD_LABEL='label'
FIELD_CLIENT='client'
FIELD_AGENCY='agency'
FIELD_CONDUCTOR='conductor'
FIELD_USER_DEFINED='userDefined'
FIELD_SONG_ID='songId'
FIELD_OUTCUE='outcue'
FIELD_DESCRIPTION='description'
FIELD_ISRC='isrc'
FIELD_ISCI='isci'
FIELD_EXTERNAL_EVENT_ID='externalEventId'
FIELD_EXTERNAL_DATA='externalData'
FIELD_EXTERNAL_ANNC_TYPE='externalAnncType'

#
# Default TCP port for connecting to Rivendell's PAD service
#
PAD_TCP_PORT=34289

class Update(object):
    def __init__(self,pad_data):
        self.__fields=pad_data;

    def __fromIso8601(self,string):
        try:
            return datetime.datetime.strptime(string.strip()[:19],'%Y-%m-%dT%H:%M:%S')
        except AttributeError:
            return ''

    def __escapeXml(self,string):
        string=string.replace("&","&amp;")
        string=string.replace("<","&lt;")
        string=string.replace(">","&gt;")
        string=string.replace("'","&apos;")
        string=string.replace("\"","&quot;")
        return string

    def __escapeWeb(self,string):
        string=string.replace("%","%25")
        string=string.replace(" ","%20")
        string=string.replace("<","%3C")
        string=string.replace(">","%3E")
        string=string.replace("#","%23")
        string=string.replace("\"","%22")
        string=string.replace("{","%7B")
        string=string.replace("}","%7D")
        string=string.replace("|","%7C")
        string=string.replace("\\","%5C")
        string=string.replace("^","%5E")
        string=string.replace("[","%5B")
        string=string.replace("]","%5D")
        string=string.replace("`","%60")
        string=string.replace("\a","%07")
        string=string.replace("\b","%08")
        string=string.replace("\f","%0C")
        string=string.replace("\n","%0A")
        string=string.replace("\r","%0D")
        string=string.replace("\t","%09")
        string=string.replace("\v","%0B")
        return string

    def __escapeJson(self,string):
        string=string.replace("\\","\\\\")
        string=string.replace("\"","\\\"")
        string=string.replace("/","\\/")
        string=string.replace("\b","\\b")
        string=string.replace("\f","\\f")
        string=string.replace("\n","\\n")
        string=string.replace("\r","\\r")
        string=string.replace("\t","\\t")
        return string

    def __replaceWildcard(self,wildcard,sfield,stype,string,esc):
        try:
            if isinstance(self.__fields['padUpdate'][stype][sfield],unicode):
                string=string.replace('%'+wildcard,self.escape(self.__fields['padUpdate'][stype][sfield],esc))
            else:
                string=string.replace('%'+wildcard,str(self.__fields['padUpdate'][stype][sfield]))
        except TypeError:
            string=string.replace('%'+wildcard,'')
        except KeyError:
            string=string.replace('%'+wildcard,'')
        return string

    def __replaceWildcardPair(self,wildcard,sfield,string,esc):
        string=self.__replaceWildcard(wildcard,sfield,'now',string,esc);
        string=self.__replaceWildcard(wildcard.upper(),sfield,'next',string,esc);
        return string;

    def __findDatetimePattern(self,pos,wildcard,string):
        start=string.find('%'+wildcard+'(',pos)
        if start>=0:
            end=string.find(")",start+3)
            if end>0:
                return (end+2,string[start:end+1])
        return None

    def __replaceDatetimePattern(self,string,pattern):
        stype='now'
        if pattern[1]=='D':
            stype='next'
        try:
            dt=self.__fromIso8601(self.__fields['padUpdate'][stype]['startDateTime'])
        except TypeError:
            string=string.replace(pattern,'')
            return string

        dt_pattern=pattern[3:-1]

        try:
            dt_pattern=dt_pattern.replace('dddd',dt.strftime('%A'))
            dt_pattern=dt_pattern.replace('ddd',dt.strftime('%a'))
            dt_pattern=dt_pattern.replace('dd',dt.strftime('%d'))
            dt_pattern=dt_pattern.replace('d',str(dt.day))

            dt_pattern=dt_pattern.replace('MMMM',dt.strftime('%B'))
            dt_pattern=dt_pattern.replace('MMM',dt.strftime('%b'))
            dt_pattern=dt_pattern.replace('MM',dt.strftime('%m'))
            dt_pattern=dt_pattern.replace('M',str(dt.month))

            dt_pattern=dt_pattern.replace('yyyy',dt.strftime('%Y'))
            dt_pattern=dt_pattern.replace('yy',dt.strftime('%y'))

            miltime=(dt_pattern.find('ap')<0)and(dt_pattern.find('AP')<0)
            if not miltime:
                if dt.hour<13:
                    dt_pattern=dt_pattern.replace('ap','am')
                    dt_pattern=dt_pattern.replace('AP','AM')
                else:
                    dt_pattern=dt_pattern.replace('ap','pm')
                    dt_pattern=dt_pattern.replace('AP','PM')
            if miltime:
                dt_pattern=dt_pattern.replace('hh',dt.strftime('%H'))
                dt_pattern=dt_pattern.replace('h',str(dt.hour))
            else:
                dt_pattern=dt_pattern.replace('hh',dt.strftime('%I'))
                hour=dt.hour
                if hour==0:
                    hour=12
                dt_pattern=dt_pattern.replace('h',str(hour))

            dt_pattern=dt_pattern.replace('mm',dt.strftime('%M'))
            dt_pattern=dt_pattern.replace('m',str(dt.minute))

            dt_pattern=dt_pattern.replace('ss',dt.strftime('%S'))
            dt_pattern=dt_pattern.replace('s',str(dt.second))
        except AttributeError:
            string=string.replace(pattern,'')
            return string

        string=string.replace(pattern,dt_pattern)
        return string

    def __replaceDatetimePair(self,string,wildcard):
        pos=0
        pattern=(0,'')
        while(pattern!=None):
            pattern=self.__findDatetimePattern(pattern[0],wildcard,string)
            if pattern!=None:
                string=self.__replaceDatetimePattern(string,pattern[1])
        return string

    def dateTimeString(self):
        """
           Returns the date-time of the update in ISO 8601 format (string).
        """
        return self.__fields['padUpdate']['dateTime']

    def dateTime(self):
        """
           Returns the date-time of the PAD update (datetime)
        """
        return self.__fromIso8601(pad_data['padUpdate']['dateTime'])

    def escape(self,string,esc):
        """
           Returns an 'escaped' version of the specified string.
           Take two arguments:

           string - The string to be processed.

           esc - The type of escaping to be applied. The following values
                 are valid:
                 PyPAD.ESCAPE_JSON - Escaping for JSON string values
                 PyPAD.ESCAPE_NONE - No escaping applied
                 PyPAD.ESCAPE_URL - Escaping for using in URLs
                 PyPAD.ESCAPE_XML - Escaping for use in XML
        """
        if(esc==0):
            return string
        if(esc==1):
            return self.__escapeXml(string)
        if(esc==2):
            return self.__escapeWeb(string)
        if(esc==3):
            return self.__escapeJson(string)
        raise ValueError('invalid esc value')

    def logMachine(self):
        """
           Returns the log machine number to which this update pertains
           (integer).
        """
        return self.__fields['padUpdate']['logMachine']

    def onairFlag(self):
        """
           Returns the state of the on-air flag (boolean).
        """
        return self.__fields['padUpdate']['onairFlag']

    def hasService(self):
        """
           Indicates if service information is included with this update
           (boolean).
        """
        try:
            return self.__fields['padUpdate']['service']!=None
        except TypeError:
           return False;
        
    def serviceName(self):
        """
           Returns the name of the service associated with this update (string).
        """
        return self.__fields['padUpdate']['service']['name']

    def serviceDescription(self):
        """
           Returns the description of the service associated with this update
           (string).
        """
        return self.__fields['padUpdate']['service']['description']

    def serviceProgramCode(self):
        """
           Returns the Program Code of the service associated with this update
           (string).
        """
        return self.__fields['padUpdate']['service']['programCode']

    def hasLog(self):
        """
           Indicates if log information is included with this update
           (boolean).
        """
        try:
            return self.__fields['padUpdate']['log']!=None
        except TypeError:
            return False;
        
    def logName(self):
        """
           Returns the name of the log associated with this update (string).
        """
        return self.__fields['padUpdate']['log']['name']

    def resolvePadFields(self,string,esc):
        """
           Takes two arguments:

           string - A string containing one or more PAD wildcards, which it
                    will resolve into the appropriate values. See the
                    'Metadata Wildcards' section of the Rivendell Operations
                    Guide for a list of recognized wildcards.

           esc - Character escaping to be applied to the PAD fields.
                 Must be one of the following:

                 PyPAD.ESCAPE_NONE - No escaping
                  PyPAD.ESCAPE_XML - "XML" escaping: Escape reserved
                                     characters as per XML-v1.0
                  PyPAD.ESCAPE_URL - "URL" escaping: Escape reserved
                                     characters as per RFC 2396
                                     Section 2.4
                 PyPAD.ESCAPE_JSON - "JSON" escaping: Escape reserved
                                     characters as per ECMA-404.
        """
        string=self.__replaceWildcardPair('a','artist',string,esc)
        string=self.__replaceWildcardPair('b','label',string,esc)
        string=self.__replaceWildcardPair('c','client',string,esc)
        string=self.__replaceDatetimePair(string,'d') # %d(<dt>) Handler
        string=self.__replaceDatetimePair(string,'D') # %D(<dt>) Handler
        string=self.__replaceWildcardPair('e','agency',string,esc)
        #string=self.__replaceWildcardPair('f',sfield,string,esc) # Unassigned
        string=self.__replaceWildcardPair('g','groupName',string,esc)
        string=self.__replaceWildcardPair('h','length',string,esc)
        string=self.__replaceWildcardPair('i','description',string,esc)
        string=self.__replaceWildcardPair('j','cutNumber',string,esc)
        #string=self.__replaceWildcardPair('k',sfield,string,esc) # Start time for rdimport
        string=self.__replaceWildcardPair('l','album',string,esc)
        string=self.__replaceWildcardPair('m','composer',string,esc)
        string=self.__replaceWildcardPair('n','cartNumber',string,esc)
        string=self.__replaceWildcardPair('o','outcue',string,esc)
        string=self.__replaceWildcardPair('p','publisher',string,esc)
        #string=self.__replaceWildcardPair('q',sfield,string,esc) # Start date for rdimport
        string=self.__replaceWildcardPair('r','conductor',string,esc)
        string=self.__replaceWildcardPair('s','songId',string,esc)
        string=self.__replaceWildcardPair('t','title',string,esc)
        string=self.__replaceWildcardPair('u','userDefined',string,esc)
        #string=self.__replaceWildcardPair('v',sfield,string,esc) # Length, rounded down
        #string=self.__replaceWildcardPair('w',sfield,string,esc) # Unassigned
        #string=self.__replaceWildcardPair('x',sfield,string,esc) # Unassigned
        string=self.__replaceWildcardPair('y','year',string,esc)
        #string=self.__replaceWildcardPair('z',sfield,string,esc) # Unassigned
        string=string.replace('\\b','\b')
        string=string.replace('\\f','\f')
        string=string.replace('\\n','\n')
        string=string.replace('\\r','\r')
        string=string.replace('\\t','\t')
        return string

    def hasPadType(self,pad_type):
        """
           Indicates if this update includes the specified PAD type
           Takes one argument:
              pad_type - The type of PAD value. Valid values are:
                         PyPAD.NOW - Now playing data
                         PyPAD.NEXT - Next to play data
        """
        try:
            return self.__fields['padUpdate'][pad_type]!=None
        except TypeError:
            return False;

    def startDateTime(self,pad_type):
        """
           Returns the start datetime of the specified PAD type
           Takes one argument:
              pad_type - The type of PAD value. Valid values are:
                         PyPAD.NOW - Now playing data
                         PyPAD.NEXT - Next to play data
        """
        try:
            return self.__fromIso8601(self.__fields['padUpdate'][pad_type]['startDateTime'])
        except AttributeError:
            return None

    def padField(self,pad_type,pad_field):
        """
           Returns the raw value of the specified PAD field.
           Takes two arguments:
              pad_type - The type of PAD value. Valid values are:
                         PyPAD.NOW - Now playing data
                         PyPAD.NEXT - Next to play data

              pad_field - The specific field. Valid values are:
                          PyPAD.FIELD_AGENCY - The 'Agency' field (string)
                          PyPAD.FIELD_ALBUM - The 'Album' field (string)
                          PyPAD.FIELD_ARTIST - The 'Artist' field (string)
                          PyPAD.FIELD_CART_NUMBER - The 'Cart Number' field
                                                    (integer)
                          PyPAD.FIELD_CART_TYPE - 'The 'Cart Type' field
                                                  (string)
                          PyPAD.FIELD_CLIENT - The 'Client' field (string)
                          PyPAD.FIELD_COMPOSER - The 'Composer' field (string)
                          PyPAD.FIELD_CONDUCTOR - The 'Conductor' field (string)
                          PyPAD.FIELD_DESCRIPTION - The 'Description' field
                                                    (string)
                          PyPAD.FIELD_EXTERNAL_ANNC_TYPE - The 'EXT_ANNC_TYPE'
                                                           field (string)
                          PyPAD.FIELD_EXTERNAL_DATA - The 'EXT_DATA' field
                                                      (string)
                          PyPAD.FIELD_EXTERNAL_EVENT_ID - The 'EXT_EVENT_ID'
                                                          field (string)
                          PyPAD.FIELD_GROUP_NAME - The 'GROUP_NAME' field
                                                   (string)
                          PyPAD.FIELD_ISRC - The 'ISRC' field (string)
                          PyPAD.FIELD_ISCI - The 'ISCI' field (string)
                          PyPAD.FIELD_LABEL - The 'Label' field (string)
                          PyPAD.FIELD_LENGTH - The 'Length' field (integer)
                          PyPAD.FIELD_OUTCUE - The 'Outcue' field (string)
                          PyPAD.FIELD_PUBLISHER - The 'Publisher' field (string)
                          PyPAD.FIELD_SONG_ID - The 'Song ID' field (string)
                          PyPAD.FIELD_START_DATETIME - The 'Start DateTime field
                                                       (string)
                          PyPAD.FIELD_TITLE - The 'Title' field (string)
                          PyPAD.FIELD_USER_DEFINED - 'The 'User Defined' field
                                                      (string)
                          PyPAD.FIELD_YEAR - The 'Year' field (integer)
        """
        return self.__fields['padUpdate'][pad_type][pad_field]




class Receiver(object):
    def __init__(self):
        self.__callback=None

    def __PyPAD_Process(self,pad):
        self.__callback(pad)

    def setCallback(self,cb):
        """
           Set the processing callback.
        """
        self.__callback=cb

    def start(self,hostname,port):
        """
           Connect to a Rivendell system and begin processing PAD events.
           Once started, a PyPAD object can be interacted with
           only within one of its callback methods.
           Takes the following arguments:

           hostname - The hostname or IP address of the Rivendell system.

           port - The TCP port to connect to. For most cases, just use
                  'PyPAD.PAD_TCP_PORT'.
        """
        sock=socket.socket(socket.AF_INET)
        conn=sock.connect((hostname,port))
        c=""
        line=""
        msg=""

        while 1<2:
            c=sock.recv(1)
            line+=c
            if c[0]=="\n":
                msg+=line
                if line=="\r\n":
                    self.__PyPAD_Process(Update(json.loads(msg)))
                    msg=""
                line=""

