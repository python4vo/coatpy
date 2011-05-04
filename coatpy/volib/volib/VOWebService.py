'''
Created on Mar 13, 2011

This class is the base class for other VO classes.
Based on version 2006-06-18 by Shui Hung Kwok

@author: shkwok
'''

from urlparse import urlparse, urlunparse
from urllib import urlencode
from urllib2 import urlopen
#from votable.VOTable import VOTable
from .. import VOTable

class VOWebService (object):
    def __init__ (self, url):
        ''' 
        All derived classes have an access url
        '''
        self.url = url
        '''parsed url = (scheme, netloc, path, params, query, fragment)'''
        self.parsedurl = urlparse (url)
        self.votable = None
    
    def buildQuery (self, parmList):
        '''    
        parmList is a dict of name/value pairs
        Returns a complete URL with query string.
        '''
        urlTuple = [ x for x in self.parsedurl ]
        qstr = urlTuple[4]
        q1 = {}
        for elm in qstr.split ('&'):
            pair = elm.split ('=')
            l = len (pair)
            if l == 0: continue
            else:
                name = pair[0]
                if len (name) == 0 : continue
                if l == 1: 
                    val = ''
                else :
                    val = pair[1]
                q1.setdefault (name, val)
        q1.update (parmList)
        urlTuple[4] = urlencode (q1)
        return urlunparse (urlTuple)

    def getRaw (self, **kwds):
        '''    
        Given the parameter list as:
        RA=ra, DEC=dec, SR=sr, VERB=verb, ...
        Returns the raw result, ie. xml in plain text
        '''
        query = self.buildQuery (kwds)
        self.hcon = urlopen (query)
        res = self.hcon.read ()
        self.hcon.close ()
        return res

    def getVOTable (self, **kwds):
        '''    
        Given the parameter list as:
        RA=ra, DEC=dec, SR=sr, VERB=verb, ...
        Returns the result as VOTable 
        '''
        query = self.buildQuery (kwds)
        self.votable = VOTable ()
        self.votable.parseFromFile(query)
        #print 'query', query
        return self.votable

