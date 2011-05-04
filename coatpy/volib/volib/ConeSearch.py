'''
Created on Mar 15, 2011

Class to handle Cone Search according to NVO
    Based on version 2005-06-01 by Shui Hung Kwok
    

@author: shkwok

'''

import sys
#from VOWebService import VOWebService
from . import VOWebService

class ConeSearch (VOWebService):
    
    def __init__ (self, url=''):
        VOWebService.__init__ (self, url)

    def buildQuery (self, parmList):
        mustParams = ["RA", "DEC", "SR"]
        for p in mustParams:
            if not p in parmList:
                raise Exception ("Parameter '%s' missing" % p)
        return VOWebService.buildQuery (self, parmList)
    
    def output2CSV (self, votable, writer=sys.stdout.write):
        idOrName = votable.getIdOrName()
        fields = votable.getFields()
        buf = []
        for fd in fields:
            attrs = fd.getAttributes ()
            name = attrs.get (idOrName)
            buf.append(name)
        writer (",".join(buf))
        writer ("\n")
        rows = votable.getTableData ()    
        for row in rows:
            flist = []
            cells = row.getChildren ("TD")
            for cell in cells:
                flist.append(cell.getContent ())
            writer (",".join(flist))
            writer ("\n")
