'''
Created on Mar 13, 2011

VOTable class

@author: shkwok
'''
#from xparser.XParser import XParser
from .. import XParser
import sys

class VOTable (object):

    def __init__ (self):
        ''' 
        Constructor, opens file if fname provided 
        '''
        pass

    def parseFromFile (self, n):
        ''' 
        Opens and parses the XML document 
        '''
        self.name = n
        xp = XParser ()
        try:
            xp.openInputFile (n)
            self.root = xp.parse()
        except:
            self.root = None
            raise IOError, "Failed to parse VOTable"
    
    def parseFromString (self, str):
        ''' 
        Parses XML from String 
        '''
        xp = XParser ()
        try:
            xp.openFromString (str)
            self.root = xp.parse()
        except:
            self.root = None
            raise IOError, "Failed to parse VOTable from string"
    
    def getFields (self):
        ''' 
        Get Fields definitions 
        Returns list of XNodes
        '''
        table = self.root.getResource ("/VOTABLE/RESOURCE/TABLE")
        return table.getChildren ("FIELD")
    
    def getColumnIdx (self, colName):
        '''
        Returns the column index for the given column name
        '''
        try:
            fields = self.getFields ()
            if fields:
                for colnr, fld in enumerate (fields):
                    if colName in fld.getAttributes().values():
                        return colnr
        except:
            pass
        return -1
    
    def getTableData (self):
        ''' 
        Gets table data from votable
        Returns list of rows
        '''
        tableData = self.root.getResource ("/VOTABLE/RESOURCE/TABLE/DATA/TABLEDATA")
        return tableData.getChildren ("TR")

    def getIdOrName (self):
        '''
        Many services return inconsistent use of ID or Name in the fields of the VOtable
        Returns the ID or Name depending what is found first.
        '''
        fields = self.getFields()
        if len(fields) == 0:
            raise Exception ("Table has no fields")
        attrs = fields[0].getAttributes()
        if attrs:
            for elem in ('ID', 'id', 'Id', 'name', 'Name', 'NAME'):
                val = attrs.get(elem)
                if val == None:
                    continue
                return elem
        return "ID"

    def outputAsXML (self, writer=sys.stdout.write):
        ''' 
        Outputs the content as XML
        Output function: writer (str)
        '''
        votRoot = self.root.getResource ("/VOTABLE")
        votRoot.outputAsXML (writer)
# end class
