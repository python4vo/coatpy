'''
Created on Mar 12, 2011
Based on version from Feb 3, 2005

Node structure for XML parser

@author: shkwok
'''
import sys 

class XNode:

	def __init__ (self, n):
		self.name = n
		self.attributes = {}
		self.content = []
		self.metaTags = []
		self.visited = 0
	
	def addMetaTag (self, xn):
		self.metaTags.append (xn)

	def addMetaTags (self, vec):
		self.metaTags += vec

	def addContent (self, cnt):
		self.content.append (cnt)

	def getMetaTags (self):
		return self.metaTags

	def addAttribute (self, at, val):
		self.attributes[at] = val

	def addAttributes (self, ar):
		self.attributes += ar

	def getAttribute (self, at):
		return self.attributes.get (at)
	
	def getAttributes (self):
		return self.attributes

	def addNode (self, node):
		self.content.append (node)

	def isSameName (self, name1):
		''' 
		Checks if name1 is equals to tag name 
		with and without namespace prefix.
		'''
		tagName = self.name
		if tagName == name1:
			return True
		str1 = tagName.split (':')
		if len (str1) == 2:
			if name1 == str1[1]:
				return True
		return False

	def getAllChildren (self):
		'''	
		Returns a list of children nodes
		'''
		res = []
		for node in self.content:
			if isinstance (node, XNode):
				res.append (node)
		return res		

	def getChildren (self, look4):
		'''
		Returns a list of children nodes that match the given name
		'''
		res = []
		for node in self.content:
			#print "class ", node.__class__.__name__, " look4 ", look4, " node name ", node
			if node.__class__.__name__ == 'XNode':
				if node.isSameName (look4):
					res.append (node)
		return res

	def getResource (self, resStr):
		'''	
		Returns the node addressed by resStr.
		The format of resStr is: tag1/tag2/tag3...
		tagX can be tag[n] to indicate the n-th element 
		if the tag occurs more than once at a given level.
		'''
		node = self
		children = []

		if resStr.startswith('/'):
			resStr = resStr.lstrip('/')
		resArray = resStr.split ('/')
		#print "res Array ", resArray, " node name ", node.name
		
		if resArray[0] != node.name:
			return None
		
		for elem in resArray[1:]:
			tmp = elem.replace (']', '[')
			list = tmp.split ('[')
			
			name = list[0]
			#print "node ", node.name, " looking 4 ", name
			idx = 0
			if len (list) > 1:
				idx = int (list[1])
			children = node.getChildren (name)
			#print "children ", children
			nr = len (children)
			#print "nr ", nr, idx
			if idx >= nr:
				return None
			node = children[idx]
		return node

	def getResourceContent (self, name):
		'''	
		Similar to getResource, except this method returns
		the content of the addressed node instead of the node itself.
		'''
		t1 = self.getResource (name)
		if t1 == None:
			return None
		return t1.getContent ()

	
	def getContent (self):
		'''	
		Returns the content of this node without the children nodes
		'''
		out = ''
		for node in self.content:
			if node.__class__.__name__ == 'XNode':
				out = out + node.getContent ()
			else:
				if out == '': 
					out = node
				else:
					out = out + ' ' + node
		if out.startswith('<![CDATA['):
			out = out.replace('<![CDATA[', '').replace (']]>', '')
			
		return out

	def writer (self, str):
		print str,

	
	def outputXMLPart (self, writer, ident=''):
		'''	
		Recursively outputs the tree as XML
		writer is a callable with 1 parameter, writer (str)
		prefix is the indentation
		'''
		spaces = '  '
		writer (ident + '<' + self.name)

		for key, value in self.attributes.items ():
			writer (" %s='%s'" % (key, value))

		cnt = len (self.content)
		if cnt == 0: 
			writer ('/>\n')
		else:
			writer ('>\n')
			for node in self.content:
				if node.__class__.__name__ == 'XNode':
					node.outputXMLPart (writer, ident + spaces)
				else:
					writer (ident + spaces + node + '\n')
			writer (ident + '</' + self.name + '>\n')

	def outputAsXML (self, writer=sys.stdout.write):
		'''	
		Outputs the entire tree as XML.
		writer is a callable with 1 parameter, i.e. writer (str)
		'''
		if writer == None:
			writer = self.writer
		for mTag in self.metaTags:
			print mTag
		self.outputXMLPart (writer)
