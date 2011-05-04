'''
Created on Mar 9, 2011

Coordinates conversion functions

@author: shkwok
'''

def any2Decimal (str1):
    '''
    Input str1 as dd:mm:ss
    outputs degree as decimal
    '''
    def split (inStr):
        '''   
        Converts HH:MM:SS to (HH, MM, SS)
        '''
        str1 = inStr + " 0 0 0"
        str1 = str1.strip()
        out = str1.replace("h", " ").replace("m", " ").replace("s", " ").replace (":", " ").split(" ")
        return (out[0], out[1], out[2])
    
    hh, mm, ss = split (str1)
    sign = 1.0
    if hh.startswith ('-'):
        sign = -1.0
        hh = hh.replace ('-', '')
        
    try:
        hh = float (hh)
        mm = float (mm) / 60.0
        ss = float (ss) / 3600.0
        return sign * (hh + mm + ss)    
    except:
        return 0

def sexaHour2Degree (str1):
    '''
    Converts sexagecimal hour to degree
    Returns degree
    '''
    return any2Decimal (str1) * 15.0
        
def degree2Sexagecimal (deg):
    '''
    Converts deg to dd:mm:ss.sss
    Returns a string
    '''
    if deg < 0:
        t = float (-deg)
        sign = '-'
    else:
        t = float (deg)
        sign = ''
    dd = int (t)
    t = (t - dd) * 60
    mm = int (t)
    ss = (t - mm) * 60

    ssStr = "%.3f" % ss
    if int(float(ssStr)) == 60:
        ss = 0
        mm += 1
        if mm >= 60:
            mm = 0
            dd += 1
    
    ssStr = "%.3f" % ss
    if float (ssStr) < 10:
        ssStr = '0' + ssStr
    
    return "%s%02d:%02d:%s" % (sign, dd, mm, ssStr)

def hour2Sexagecimal (hour):
    '''
    Returns hour in sexagecimal string
    '''
    return degree2Sexagecimal(hour)

def normalize360 (deg):
    '''
    Returns normalized degree 0 to 360
    '''
    while deg < 0:
        deg += 360
    while deg >= 360:
        deg -= 360
    return deg

def normalize180 (deg):
    '''
    Returns normalized degree -180 to 180
    '''
    deg = normalize360(deg)
    if deg > 180:
        return deg - 360
    return deg