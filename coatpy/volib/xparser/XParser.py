'''
Created on Mar 12, 2011
Based on XParser from May 19, 2005

XParser

@author: shkwok
'''

#from xparser import XNode
from . import XNode
from io import StringIO
from urllib2 import urlopen

''' XParser class
	First, instantiate an object:
		xparser = XParser ()
	Then get input data from either a file openInputFile(fname)
	where fname can be a URL or a local file name; or
	from openFromString (str), where str is from some other source.
		xparser.openInputFile (fname) or
		xparser.openFromString (str)
	Next call 
		root = xparser.parse ()
		root is a XNode, the root of the XML tree.
'''

class XParser:
	''' 
	Constructor with optional node class
	node should be a subclass of XNode.
	SAX parsing can be achieve by using a customized node.
	node may or may not keep the content to saving memory.
	'''
	def __init__ (self, node=XNode.XNode):
		self.nodeClass = node

	def tryOpen (self, fname):
		''' 
		If fname starts with http:// or ftp:// then
		use urlopen, otherwise open as plain file.
		'''
		lst = ('http://', 'ftp://')
		for l in lst:
			if fname.startswith (l):
				return urlopen (fname)
		else:
			return open (fname, 'r')
			
	def openInputFile (self, fname):
		self.blen = 0
		self.lineNr = 0
		self.column = 0
		try:
			self.fh = self.tryOpen (fname)
			return self.fh
		except:
			raise IOError, 'Failed to open %s' % fname

	def openFromString (self, inputStr):
		self.blen = 0
		self.lineNr = 0
		self.column = 0
		self.fh = StringIO (inputStr)

	def readChar (self):
		''' 
		Reads one char from self.fh
		Fills the input buffer if necessary.
		Sets column and lineNr for reporting.
		'''
		if self.column == self.blen:
			self.buffer = self.fh.readline (65535)
			self.column = 0
			self.blen = len (self.buffer)
			self.lineNr += 1
			if self.blen == 0:
				return False
		
		c = self.buffer[self.column]
		self.column += 1
		return c

	def getLineNrStr (self):
		''' 
		Reports lineNr and column with of the error.
		'''
		return ('[%d,%d] %s\n' % (self.lineNr, self.column, self.buffer))
	
	def xgetToken (self):
		''' 
		Help function for debugging 
		'''
		t = self.xgetToken ()
		#print 'xget (%s)' % t
		return t

	def getBodyToken (self):
		''' 
		Reads everything until end of tag, which starts with '<'
		'''
		state = 0
		sb = ''
		while self.currChar != False:
			if state == 0:
				if self.currChar == '<':
					return ''.join (sb)
				elif self.currChar in (' ', '\n', '\t', '\r'):
					sb += ' '
				else:
					sb += self.currChar

			x = self.readChar ()
			if x == False:
				if len (sb) > 0: return sb
				else: return False
			
			self.currChar = x
		# while
		return False
				
	def getToken (self):	
		''' 
		Reads a token
		Called while reading inside a tag. 
		'''
		state = 0
		waitFor = ' '
		c1 = 0
		sb = ''
				
		while self.currChar != False:
			#print 'state', state, self.currChar
			if state == 0:
				if self.currChar in (' ', '\n', '\r', '\t'):
					pass
				elif self.currChar == '<':
					state = 1
					sb = sb + self.currChar
				elif self.currChar in ('=', '>', '[', ']'):
					c1 = self.currChar
					self.currChar = self.readChar ()
					return c1
				elif self.currChar in ('/', '?'):
					state = 3
					sb = sb + self.currChar
				elif self.currChar in ('\'', '"'):
					waitFor = self.currChar
					state = 4
					sb = ''
				elif self.currChar == '-':
					sb = sb + self.currChar
					state = 5
				else:
					sb = sb + self.currChar
					state = 2
			elif state == 1: #  got '<', can be <, </, < ?, <!
				if self.currChar in ('?', '!', '/'):
					sb += self.currChar
					self.currChar = self.readChar ()
				return sb
			elif state == 2: # a string
				if self.currChar in (' ', '\n', '\r', '\t'):
					self.currChar = self.readChar ()
					return sb
				elif self.currChar in ('/', '?'):
					return sb
				elif self.currChar in ('<', '>', '=', '[', '-'):
					return sb
				else:
					sb += self.currChar
			elif state == 3: # got '/' or '?'
				if self.currChar == '>':
					sb += self.currChar
					self.currChar = self.readChar ()
					return sb
				elif self.currChar == '<':
					return sb
				else:
					# '/' or '?' not followed by '>'
					sb += self.currChar
					state = 2 # is a string
			elif state == 4: # got ' or '
				if self.currChar == waitFor:
					self.currChar = self.readChar ()
					return sb
				else:	
					sb += self.currChar
					#break
			elif state == 5: # got '-'
				if self.currChar == '-':
					sb += self.currChar
					self.currChar = self.readChar ()
					return sb
				elif self.currChar in ('?', '<', '>', '!'):
					return '-'
				else:
					state = 2
					sb += self.currChar
			x = self.readChar ()
			if x == False:
				if len (sb) > 0: return sb
				else: return False
			
			self.currChar = x
		# while
		return False
	# getToken
	
	def getComment (self):
		''' 
		Reads a comment <!-- ... -->
		'''
		state = 99
		sb = ''
		
		while self.currChar != False:
			if state == 0: 
				if self.currChar == '-':
					state = 1
				else:
					sb += self.currChar
			elif state == 1: # --
				if self.currChar == '-':
					state = 2
				else:
					sb += '-'.self.currChar
					state = 0
			elif state == 2:
				if self.currChar == '>':
					# got '-.'
					self.currChar = self.readChar ()
					return sb
				else:
					sb += '--'.self.currChar
					state = 0
			elif state == 99:
				if self.currChar in (' ', '\n', '\r', '\t'):
					state = 0
					sb += self.currChar
			self.currChar = self.readChar ()
		return False
	# getComment

	def getCDATA (self):
		''' 
		Reads CDATA 
		'''
		state = 0
		sb = ''
		
		while self.currChar != False:
			if state == 0:
				if self.currChar == ']':
					state = 1
				else:
					sb += self.currChar
			elif state == 1:
				if self.currChar == ']':
					state = 2
				else:
					sb += ']' + self.currChar
					state = 0
			elif state == 2:
				if self.currChar == '>':
					self.currChar = self.readChar ()
					return sb
				else:
					state = 0
					sb += ']]' + self.currChar
			else:
				sb += self.currChar
			
			x = self.readChar ()
			if x == False:
				return sb
			
			self.currChar = x
		
		return False	 
	# getCDATA
	
	'''
	The grammar is:
	Root ::= Tag
	Tag	::= TagStart Body TagEnd
	TagStart ::= '<' 'name' AttList '>'
	TagEnd	::= '</' 'name' '>'
	Attribute ::= 'name' '=' 'value' 
	AttList	::= Attribute | Attribute AttList | e
	Body ::= StringList | TagList
	StringList ::= 'string' | 'string' StringList | e
	TagList	::= Tag | TabList | e
	e ::= ''
	'''
	
	def parseXTag (self, token):
		''' 
		Reads tag starting with '<?'
		These are tags at the beginning of a xml document.
		'''
		str = ''

		if token != '<?' and token != '<!':
			print 'Error token, ? or <! expected\n'
			return False
		
		str += token
		str += self.currChar

		c = self.readChar ()
		str += c
		while self.currChar != False and c != '>':
			c = self.readChar ()
			str += c
		
		self.currChar = self.readChar ()
		return str
	# parseXTag
	
	def parseTagStart (self, token):
		''' 
		Reads start of tags 
		Checks if CDATA or comment
		then reads attributes
		checks if ends with '/>'
		'''	
		
		value = ''
		
		self.tagClosed = 0
		if not token in ('<', '<!', '<?'): 
			print 'Error token %s, < expected\n%s' % \
				(token, self.getLineNrStr ())
			self.tagClosed = 1
			return False
		
		firstToken = token
		token = self.getToken ()
			
		if token == '[':
			token = self.getToken ()
			if token == 'CDATA':
				token = self.getToken ()
				if token == '[':
					cdData = self.nodeClass ('[CDATA[')
					token = self.getCDATA ()
					cdData.addNode (token)
					self.tagClosed = 1
					return cdData
		if token == '--' and firstToken == '<!':
			comments = self.nodeClass ('COMMENT')
			token = self.getComment ()
			comments.addNode (token)
			self.tagClosed = 1
			return comments
		
		xn = self.nodeClass (token)
		
		''' Reads tag attributes '''
		attname = self.getToken ()
		while attname != '>' and attname != '/>':
			token = self.getToken ()
			if token == '=':
				value = self.getToken ()
				xn.addAttribute (attname, value)
				#print 'Added att ', attname, value, ' to ', xn.name
				attname = self.getToken ()
			else:
				xn.addAttribute (attname, '')
				attname = token
		
		if attname == '/>': 
			self.tagClosed = 1
		return xn
	# parseTagStart
	
	def parseTagEnd (self, xn, token):
		''' 
		Reads end of tag
		Checks that it has a matching opening tag
		'''
		if token != '</':
			print 'Error end tag token, \'</\'  expected ' + \
				self.getLineNrStr ()
		
		name = self.getToken ()
		if name != xn.name: 
			print 'End of tag ' + \
				xn.name + ' expected ' + \
				self.getLineNrStr () + ' (name)'
		token = self.getToken ()
		if token != '>':
			print 'Error > expected ' + self.getLineNrStr ()
		
		# parseTagEnd
	
	def parseBody (self, xn):
		''' 
		Reads the content of a tag until end of tag
		'''
		token = self.getBodyToken()
		while token != False:
			if token == '</':
				self.parseTagEnd (xn, token)
				return
			
			''' Two cases:
				if token starts with < then it can be end of tag
				or it can be a string.
			'''
			t1 = token.strip ()
			if len (t1) > 0:
				if t1.startswith ('<'):
					xn1 = self.parseIt (t1)
					if xn1.name == '[CDATA[':
						xn.addNode ('<![CDATA[' + xn1.content[0] + ']]>')
					elif xn1.name == 'COMMENT':
						xn.addNode ('<!--' + xn1.content[0] + '-->')
					else:
						xn.addNode (xn1)
				else:
					xn.addNode (t1)
			token = self.getToken ()
		return
	# parseBody
	
	def parseIt (self, token):
		''' 
		Convenient method for recursion.
		'''
		xn = self.parseTagStart (token)  
		if not self.tagClosed:
			self.parseBody (xn)
		return xn
	# parseIt 
	
	def parse (self):
		''' 
		Main entry point for parsing.
		'''
		metaTags = []
		self.currChar = ' '
		token = self.getToken ()
		
		while token == '<?' or token == '<!':
			metaTags.append (self.parseXTag (token))
			token = self.getToken ()
		# while 
		xn = self.parseTagStart (token)
		if xn == False: 
			return False
		xn.addMetaTags (metaTags)
		self.parseBody (xn)
		self.fh.close ()
		return xn
	# parse
	
	def parseFromFile (self, fname):
		self.openInputFile(fname)
		return self.parse()
	
	def parseFromString (self, str):
		self.openFromString(str)
		return self.parse()
# XParser
