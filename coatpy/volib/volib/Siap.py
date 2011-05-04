'''
Created on Mar 13, 2011

SIAP class to handle SIAP queries.

@author: shkwok

    Based on version 2005-06-03 by Shui Hung Kwok

    Image generation parameters:
    See http://www.ivoa.net/Documents/WD/SIA/sia-20040524.html

    MUST parameters are:
    RA Right ascension in decimal degree
    DEC declination in decimal degree
    SIZE search window in decimal degree
    VERB = [0,4]

    FORMAT: 
        GRAPHIC
        METADATA
        ALL
        one of image/fits, image/jpeg, image/gif, image/png

    INTERSECT: optional
        COVERS
        CENTERS
        ENCLOSED
        OVERLAPS, default

    Image generation optional parameters: (haven't tested these)

    NAXIS
    The size of the output image in pixels. 
    This is a vector-valued quantity, expressed as "NAXIS=<width>,<height>". 
    If only one value is given it applies to both image axes. 
    Default: determined from the ROI (see below). 
    This is the only image generation parameter likely be supported by a cutout service.

    CFRAME
    The coordinate system reference frame, selected from ICRS, 
    FK5, FK4, ECL, GAL, and SGAL (these abbreviations follow CDS Aladin). 
    Default: ICRS.

    EQUINOX
    Epoch of the mean equator and equinox for the specified coordinate 
    system reference frame (CFRAME).  Not required for ICRS. 
    Default: B1950 for FK4, otherwise J2000.

    CRPIX
    The coordinates of the reference pixel, expressed in the pixel 
    coordinates of the output image, with [1,1] being the center of the 
    first pixel of the first row of the image. 
    This is a vector-valued quantity; if only one value is given it 
    applies to both image axes. 
    Default: the image center.

    CRVAL
    The world coordinates relative to CFRAME at the reference pixel. 
    This is a vector-valued quantity; both array values are required. 
    Default: the region center coordinates (POS) at the center of the image, 
    transformed to the output coordinate system reference frame if other 
    than ICRS. If CRPIX is specified to be other than the image center 
    the corresponding CRVAL can be computed, but should be specified explicitly by the client.

    CDELT
    The scale of the output image in decimal degrees per pixel. 
    A negative value implies an axis flip. Since the default image 
    orientation is N up and E to the left, the default sign of 
    CDELT is [-1,1]. This is a vector-valued quantity; 
    if only one value is given it applies to both image axes, with the 
    sign defaulting as specified above. 
    Default: implied (see below), otherwise service-specific.

    ROTANG
    The rotation angle of the image in degrees relative to CFRAME 
    (an image which is unrotated in one reference frame may be rotated in another). 
    This is the rotation of the WCS declination or latitude axis 
    with respect to the second axis of the image, measured 
    in the counterclockwise direction (as for FITS WCS, 
    which is in turn based on the old AIPS convention). 
    Default: 0 (no rotation).

    PROJ
    The celestial projection of the output image expressed as a three-character 
    code as for FITS WCS, e.g., "TAN", "SIN", "ARC", and so forth. Default: TAN.

'''

#from volib.VOWebService import VOWebService
from . import VOWebService
from urllib2 import urlopen

class Siap (VOWebService):
    def __init__ (self, url):
        VOWebService.__init__ (self, url)

    def buildQuery (self, parmList):
        '''    
        Checks that parmList has all the necessary parameters for SIAP.
        Keyword parameters are:
            POS, RA, DEC, FORMAT, SIZE
        If POS is present, then use it.
        If POS is not present then RA/DEC must be present.
        Otherwise raise exception.
        Returns a query url
        '''
        pos = parmList.get ('POS', None)
        if pos == None:
            ra = parmList.get ('RA', None)
            dec = parmList.get ('DEC', None)
            if (ra == None) or (dec == None):
                raise Exception ('Position parameter missing')
            pos = "%s,%s" % (ra, dec)
            parmList.setdefault ('POS', pos)
            # make sure RA/DEC are defined and delete them
            # so no exception is thrown
            parmList.setdefault ("RA", ra)
            parmList.setdefault ("DEC", dec)
            del parmList["RA"]
            del parmList["DEC"]

        format = parmList.get ('FORMAT', 'all')
        parmList.setdefault ('FORMAT', format)

        size = parmList.get ('SIZE', '0.05')
        parmList.setdefault ('SIZE', size)
        return VOWebService.buildQuery (self, parmList)

    def getImageURLs (self, ra, dec, size, verb=0, format="image/fits"):
        '''
        Returns the url corresponding to the desired image
        '''
        vot = self.getVOTable (RA=ra, DEC=dec, SIZE=size, 
            FORMAT=format, VERB=verb)

        # Get column index for access url
        urlColIdx = vot.getColumnIdx ('VOX:Image_AccessReference')
        formatIdx = vot.getColumnIdx ('VOX:Image_Format')
        if urlColIdx < 0:
            raise Exception, "No access reference found"
        
        urls = []
        for row in vot.getTableData ():
            #print "row ", row
            #row.outputAsXML()
            cells = row.getChildren ("TD")
            url = cells[urlColIdx].getContent()
            fmt = cells[formatIdx].getContent()
            print "url ", url, " fmt ", fmt

            if fmt == format:
                urls.append (url)
        return urls
        
def saveImageAs (url, fname):
    ''' 
    Retrieves image from the given url and save it to fname
    '''
    print "opening ", url
    inp = urlopen (url)
    try:
        outp = file (fname, "wb")
        outp.write (inp.read ())
    except Exception:
        print "Failed to retrieve image from ", url
    inp.close ()
    outp.close ()


