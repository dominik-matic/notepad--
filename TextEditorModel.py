from Location import Location
from LocationRange import LocationRange
from CursorObserver import CursorObserver
from TextObserver import TextObserver
from UndoManager import UndoManager
from EditActionImpl import DeleteEditAction, InsertEditAction

class TextEditorModel:
	def __init__(self, text: str):
		self.lines = text.split('\n')
		self.selectionRange = None
		self.cursorLocation = Location(len(self.lines[len(self.lines) - 1]), len(self.lines) - 1)
		self.cursorObservers = []
		self.textObservers = []

	def allLines(self):
		return iter(self.lines)

	def linesRange(self, index1: int, index2: int):
		return iter(self.lines[index1:index2])

	def subscribeCursorObserver(self, obs: CursorObserver):
		self.cursorObservers.append(obs)

	def unsubscribeCursorObserver(self, obs: CursorObserver):
		self.cursorObservers.remove(obs)

	def subscribeTextObserver(self, obs: TextObserver):
		self.textObservers.append(obs)
	
	def unsubscribeTextObserver(self, obs: TextObserver):
		self.textObservers.remove(obs)	

	def notifyCursorObservers(self):
		for obs in self.cursorObservers:
			obs.updateCursorLocation(self.cursorLocation)

	def notifyTextObservers(self):
		for obs in self.textObservers:
			obs.updateText()

	def moveCursorLeft(self, notify = True):
		if(self.selectionRange is not None and notify):
			self.cancelSelection('L')
			return False
		newX = self.cursorLocation.x - 1
		if(newX >= 0):
			self.cursorLocation.x = newX
			self.notifyCursorObservers()
			return True
		elif(self.cursorLocation.y - 1 >= 0):
			newY = self.cursorLocation.y - 1
			newX = len(self.lines[newY])
			self.cursorLocation.x = newX
			self.cursorLocation.y = newY
			if notify: self.notifyCursorObservers()
			return True
		return False

	def moveCursorRight(self, notify = True):
		if(self.selectionRange is not None and notify):
			self.cancelSelection('R')
			return False
		newX = self.cursorLocation.x + 1
		if(newX <= len(self.lines[self.cursorLocation.y])):
			self.cursorLocation.x = newX
			if notify: self.notifyCursorObservers()
			return True
		elif(self.cursorLocation.y + 1 < len(self.lines)):
			newY = self.cursorLocation.y + 1
			self.cursorLocation.x = 0
			self.cursorLocation.y = newY
			if notify: self.notifyCursorObservers()
			return True
		return False

	def moveCursorUp(self, notify = True):
		if(self.selectionRange is not None and notify):
			self.cancelSelection()
		newY = self.cursorLocation.y - 1
		if(newY >= 0):
			self.cursorLocation.y = newY
			self.cursorLocation.x = self.cursorLocation.x if self.cursorLocation.x <= len(self.lines[newY]) else len(self.lines[newY])
			if notify: self.notifyCursorObservers()
			return True
		return False

	def moveCursorDown(self, notify = True):
		if(self.selectionRange is not None and notify):
			self.cancelSelection()
		newY = self.cursorLocation.y + 1
		if(newY < len(self.lines)):
			self.cursorLocation.y = newY
			self.cursorLocation.x = self.cursorLocation.x if self.cursorLocation.x <= len(self.lines[newY]) else len(self.lines[newY])
			if notify: self.notifyCursorObservers()
			return True
		return False
	
	#############################
	#############################
	#############################
	def deleteBefore(self):
		if(self.selectionRange is not None):
			UndoManager.instance().push(
				DeleteEditAction(self, self.selectionRange.start, self.selectionRange.end, self.getSelectedText(), 'end')
			)
			self.deleteRange(self.selectionRange)
			return
		x, y = self.cursorLocation.get()
		if(x == 0 and y == 0):
			return
		if(x == 0):
			UndoManager.instance().push(
				DeleteEditAction(self, Location(len(self.lines[y - 1]), y - 1), Location(0, y), '\n', 'end')
			)
			self.moveCursorLeft(notify=False)
			self.lines[y - 1] = self.lines[y - 1] + self.lines[y]
			del self.lines[y]
			self.notifyTextObservers()
			self.notifyCursorObservers()
		else:
			UndoManager.instance().push(
				DeleteEditAction(self, Location(x - 1, y), Location(x, y), self.lines[y][x - 1], 'end')
			)
			self.moveCursorLeft(notify=False)
			self.lines[y] = self.lines[y][0:x - 1] + self.lines[y][x:]
			self.notifyTextObservers()
			self.notifyCursorObservers()


	#############################
	#############################
	#############################
	def deleteAfter(self):
		if(self.selectionRange is not None):
			UndoManager.instance().push(
				DeleteEditAction(self, self.selectionRange.start, self.selectionRange.end, self.getSelectedText(), 'start')
			)
			self.deleteRange(self.selectionRange)
			return
		x, y = self.cursorLocation.get()
		if(y == len(self.lines) - 1 and x == len(self.lines[y])):
			return
		
		if(x == len(self.lines[y])):
			UndoManager.instance().push(
				DeleteEditAction(self, Location(len(self.lines[y]), y), Location(0, y + 1), '\n', 'start')
			)
			self.lines[y] = self.lines[y] + self.lines[y + 1]
			del self.lines[y + 1]
			self.notifyTextObservers()
			self.notifyCursorObservers()
		else:
			UndoManager.instance().push(
				DeleteEditAction(self, Location(x, y), Location(x + 1, y), self.lines[y][x], 'start')
			)
			self.lines[y] = self.lines[y][0:x] + self.lines[y][x + 1:]
			self.notifyTextObservers()
			self.notifyCursorObservers()

	def deleteRange(self, r : LocationRange, notify=True):
		x1, y1 = r.start.get()
		x2, y2 = r.end.get()
		toDelete = []
		if(y1 == y2):
			self.lines[y1] = self.lines[y1][:x1] + self.lines[y1][x2:]
		else:
			self.lines[y1] = self.lines[y1][:x1]
			for i in range(y1 + 1, y2):
				toDelete.append(i)
			self.lines[y1] = self.lines[y1] + self.lines[y2][x2:]
			
			toDelete.append(y2)
			toDelete.reverse()
			for index in toDelete:
				del self.lines[index]

		self.selectionRange = None
		self.cursorLocation.set(x1, y1)
		if(notify):
			self.notifyTextObservers()
			self.notifyCursorObservers()

	#############################
	#############################
	#############################
	def insertChar(self, c: chr):
		if(self.selectionRange is not None):
			UndoManager.instance().push(
				DeleteEditAction(self, self.selectionRange.start, self.selectionRange.end, self.getSelectedText(), 'end')
			)
			self.deleteRange(self.selectionRange, notify=False)
		x, y = self.cursorLocation.get()

		if(ord(c) == 10):
			c = '\n'
			newLine = self.lines[y][x:]
			self.lines[y] = self.lines[y][:x]
			self.lines.insert(y + 1, newLine)
			UndoManager.instance().push(
				InsertEditAction(self, Location(x, y), Location(0, y + 1), c)
			)
		else:
			self.lines[y] = self.lines[y][:x] + c + self.lines[y][x:]
			UndoManager.instance().push(
				InsertEditAction(self, Location(x, y), Location(x + 1, y), c)
			)
		
		self.moveCursorRight(notify=False)
		self.notifyTextObservers()
		self.notifyCursorObservers()


	#############################
	#############################
	#############################
	def insert(self, s: str, notify=True, invokeUM=True):
		if(self.selectionRange is not None):
			if(invokeUM):
				UndoManager.instance().push(
					DeleteEditAction(self, self.selectionRange.start, self.selectionRange.end, self.getSelectedText(), 'end')
				)
			self.deleteRange(self.selectionRange, notify=False)
		x, y = self.cursorLocation.get()
		newLines = s.split('\n')
		newLinesIndex = 1
		leftoverLine = self.lines[y][x:]
		
		self.lines[y] = self.lines[y][:x] + newLines[0]

		for i in range(y + 1, y + len(newLines)):
			self.lines.insert(i, newLines[newLinesIndex])
			newLinesIndex = newLinesIndex + 1
		
		self.lines[y + len(newLines) - 1] = self.lines[y + len(newLines) - 1] + leftoverLine
		self.cursorLocation.set(len(self.lines[y + len(newLines) - 1]) - len(leftoverLine), y + len(newLines) - 1)
		if(invokeUM):
			UndoManager.instance().push(
				InsertEditAction(self, Location(x, y), self.cursorLocation, s)
			)
		if(notify):
			self.notifyTextObservers()
			self.notifyCursorObservers()
		
	def getSelectedText(self):
		if(self.selectionRange is None):
			return None
		text = ''
		x1, y1 = self.selectionRange.start.get()
		x2, y2 = self.selectionRange.end.get()
		if(y1 == y2):
			text = self.lines[y1][x1:x2]
		else:
			text = self.lines[y1][x1:] + '\n'
			for i in range(y1 + 1, y2):
				text = text + self.lines[i] + '\n'
			text = text + self.lines[y2][:x2]
		return text


	def getSelectionRange(self):
		return self.selectionRange

	def setSelectionRange(self, r: LocationRange):
		self.selectionRange = r
		self.notifyTextObservers()

	def shiftCursorLeft(self):
		x, y = self.cursorLocation.get()
		if(not self.moveCursorLeft(notify=False)):
			return
		if(self.selectionRange is None):
			self.selectionRange = LocationRange(Location(self.cursorLocation.x, self.cursorLocation.y), Location(x, y))
		else:
			if(x == self.selectionRange.start.x and y == self.selectionRange.start.y):
				self.selectionRange.start.set(self.cursorLocation.x, self.cursorLocation.y)
			elif(x == self.selectionRange.end.x and y == self.selectionRange.end.y):
				self.selectionRange.end.set(self.cursorLocation.x, self.cursorLocation.y)
				if(self.selectionRange.start.get() == self.selectionRange.end.get()):
					self.selectionRange = None
			else:
				print('Should never happen!')
		self.notifyTextObservers()
		self.notifyCursorObservers()

	def shiftCursorRight(self):
		x, y = self.cursorLocation.get()
		if(not self.moveCursorRight(notify=False)):
			return
		if(self.selectionRange is None):
			self.selectionRange = LocationRange(Location(x, y), Location(self.cursorLocation.x, self.cursorLocation.y))
		else:
			if(x == self.selectionRange.start.x and y == self.selectionRange.start.y):
				self.selectionRange.start.set(self.cursorLocation.x, self.cursorLocation.y)
				if(self.selectionRange.start.get() == self.selectionRange.end.get()):
					self.selectionRange = None
			elif(x == self.selectionRange.end.x and y == self.selectionRange.end.y):
				self.selectionRange.end.set(self.cursorLocation.x, self.cursorLocation.y)
			else:
				print('Should never happen!')
		self.notifyTextObservers()
		self.notifyCursorObservers()
	
	def shiftCursorUp(self):
		x, y = self.cursorLocation.get()
		if(not self.moveCursorUp(notify=False)):
			return
		if(self.selectionRange is None):
			self.selectionRange = LocationRange(Location(self.cursorLocation.x, self.cursorLocation.y), Location(x, y))
		else:
			if(x == self.selectionRange.start.x and y == self.selectionRange.start.y):
				self.selectionRange.start.set(self.cursorLocation.x, self.cursorLocation.y)
			elif(x == self.selectionRange.end.x and y == self.selectionRange.end.y):
				self.selectionRange.end.set(self.cursorLocation.x, self.cursorLocation.y)
				if(self.selectionRange.start.get() == self.selectionRange.end.get()):
					self.selectionRange = None
			else:
				print('Should never happen!')
		self.notifyTextObservers()
		self.notifyCursorObservers()

	def shiftCursorDown(self):
		x, y = self.cursorLocation.get()
		if(not self.moveCursorDown(notify=False)):
			return
		if(self.selectionRange is None):
			self.selectionRange = LocationRange(Location(x, y), Location(self.cursorLocation.x, self.cursorLocation.y))
		else:
			if(x == self.selectionRange.start.x and y == self.selectionRange.start.y):
				self.selectionRange.start.set(self.cursorLocation.x, self.cursorLocation.y)
				if(self.selectionRange.start.get() == self.selectionRange.end.get()):
					self.selectionRange = None
			elif(x == self.selectionRange.end.x and y == self.selectionRange.end.y):
				self.selectionRange.end.set(self.cursorLocation.x, self.cursorLocation.y)
			else:
				print('Should never happen!')
		self.notifyTextObservers()
		self.notifyCursorObservers()
	

	def cancelSelection(self, direction = 'X'):
		if(direction == 'L'):
			self.cursorLocation.x = self.selectionRange.start.x
			self.cursorLocation.y = self.selectionRange.start.y
			self.notifyCursorObservers()
		elif(direction == 'R'):
			self.cursorLocation.x = self.selectionRange.end.x
			self.cursorLocation.y = self.selectionRange.end.y
			self.notifyCursorObservers()
		self.selectionRange = None
		self.notifyTextObservers()
		self.notifyCursorObservers()

	def clearDocument(self):
		self.selectionRange = LocationRange(
			Location(0, 0),
			Location(len(self.lines[-1]), len(self.lines) - 1)
		) 
		self.deleteBefore()
	
	def cursorToStart(self):
		self.cursorLocation = Location(0, 0)
		self.notifyCursorObservers()

	def cursorToEnd(self):
		self.cursorLocation = Location(
			len(self.lines[-1]),
			len(self.lines) - 1
		)
		self.notifyCursorObservers()




