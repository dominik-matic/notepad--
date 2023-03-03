#!bin/python
import tkinter as tk
from tkinter import filedialog as fd
import TextEditorModel
import Location
from CursorObserver import CursorObserver
from TextObserver import TextObserver
from ClipboardStack import ClipboardStack
from UndoManager import UndoManager
from MenuBar import MenuBar
import os
import importlib

class TextEditor(tk.Tk, CursorObserver, TextObserver):
	def __init__(self, model : TextEditorModel):
		super().__init__()
		self.title('Notepad--')
		self.model = model
		self.clipboard = ClipboardStack()
		self.geometry('800x600')

		self.plugins = []
		self.loadPlugins()
		#self.eval('tk::PlaceWindow . center')

		self.menubar = MenuBar(self, self.plugins)
		self.config(menu=self.menubar)
		self.frame = tk.Frame(self)
		self.frame.pack(fill=tk.BOTH, expand=1)
		self.statusbar = tk.Label(self, relief=tk.SUNKEN, anchor=tk.E)
		self.statusbar.pack(side=tk.BOTTOM, fill=tk.X)

		self.bindInputs()
		self.model.subscribeCursorObserver(self)
		self.model.subscribeTextObserver(self)

		self.fontname = 'Liberation Mono'
		self.fontsize = 16
		self.spacing = 3
		self.offsetX = 10
		self.offsetY = 10
		self.cursorHeight = 18
		
		self.cursorId = 0
		self.canvas = tk.Canvas(self.frame)
		
		self.drawText()
		self.drawCursor()
		self.updateStatusBar()

	def drawText(self):
		self.drawHighlight()
		y = self.offsetY
		for line in self.model.allLines():
			self.canvas.create_text(self.offsetX, y,
								fill='white',
								text=line,
								anchor=tk.W,
								font=(self.fontname, self.fontsize))
			y = y + self.fontsize + self.spacing
		self.canvas.pack(fill=tk.BOTH, expand=1)

	def drawCursor(self):
		if(self.cursorId):
			self.canvas.delete(self.cursorId)
		x = self.model.cursorLocation.x
		y = self.model.cursorLocation.y
		y = self.offsetY + y * (self.fontsize + self.spacing)
		x = self.offsetX + x * (self.fontsize - 3) # mn
		self.cursorId = self.canvas.create_line(x, y - self.cursorHeight/2, x, y + self.cursorHeight/2, fill='white', width='3')
		self.canvas.pack(fill=tk.BOTH, expand=1)

	def drawHighlight(self):
		if(self.model.getSelectionRange() is None):
			return
		start = self.model.getSelectionRange().start
		end = self.model.getSelectionRange().end
		x1 = self.offsetX + start.x * (self.fontsize - 3) # magic number
		y1 = self.offsetY + start.y *(self.fontsize + self.spacing) - self.cursorHeight / 2
		if(start.y == end.y):	
			x2 = self.offsetX + end.x * (self.fontsize - 3)
			y2 = y1 + self.cursorHeight
			self.canvas.create_rectangle(x1, y1, x2, y2, fill='gray')
		else:
			x2 = self.offsetX + len(self.model.lines[start.y]) * (self.fontsize - 3)
			y2 = y1 + self.cursorHeight
			self.canvas.create_rectangle(x1, y1, x2, y2, fill='gray')
			for i in range(start.y + 1, end.y):
				x1 = self.offsetX
				y1 = self.offsetY + i * (self.fontsize + self.spacing) - self.cursorHeight / 2
				x2 = self.offsetX + len(self.model.lines[i]) * (self.fontsize - 3)
				y2 = y1 + self.cursorHeight
				self.canvas.create_rectangle(x1, y1, x2, y2, fill='gray')
			x1 = self.offsetX
			y1 = self.offsetY + end.y * (self.fontsize + self.spacing) - self.cursorHeight / 2
			x2 = self.offsetX + end.x * (self.fontsize - 3)
			y2 = y1 + self.cursorHeight
			self.canvas.create_rectangle(x1, y1, x2, y2, fill='gray')



	def bindInputs(self):
		self.bind('<Left>', lambda event: self.model.moveCursorLeft())
		self.bind('<Right>', lambda event: self.model.moveCursorRight())
		self.bind('<Up>', lambda event: self.model.moveCursorUp())
		self.bind('<Down>', lambda event: self.model.moveCursorDown())
		self.bind('<BackSpace>', lambda event: self.model.deleteBefore())
		self.bind('<Delete>', lambda event: self.model.deleteAfter())
		self.bind('<Shift-Left>', lambda event: self.model.shiftCursorLeft())
		self.bind('<Shift-Right>', lambda event: self.model.shiftCursorRight())
		self.bind('<Shift-Up>', lambda event: self.model.shiftCursorUp())
		self.bind('<Shift-Down>', lambda event: self.model.shiftCursorDown())
		self.bind('<Return>', lambda event: self.model.insertChar(chr(10)))
		self.bind('<Key>', self.keyPressed)
		self.bind('<Control-c>', self.copyText)
		self.bind('<Control-x>', self.cutText)
		self.bind('<Control-v>', self.pasteText)
		self.bind('<Control-Shift-V>', self.pasteTextAndPop)
		self.bind('<Control-C>', self.copyText)
		self.bind('<Control-X>', self.cutText)
		self.bind('<Control-V>', self.pasteText)
		self.bind('<Control-Shift-v>', self.pasteTextAndPop)
		self.bind('<Control-z>', self.undo)
		self.bind('<Control-Z>', self.undo)
		self.bind('<Control-y>', self.redo)
		self.bind('<Control-Y>', self.redo)
		
	def updateCursorLocation(self, loc: Location):
		self.drawCursor()
		self.updateStatusBar()
	
	def updateText(self):
		self.canvas.delete('all')
		self.drawText()
		self.updateStatusBar()

	def keyPressed(self, event):
		if(event.state & 0x4 == 0 and event.char):
			self.model.insertChar(event.char)
	
	def copyText(self, event=None):
		selectedText = self.model.getSelectedText()
		if(selectedText is None):
			return
		self.clipboard.push(selectedText)		

	def cutText(self, event=None):
		selectedText = self.model.getSelectedText()
		if(selectedText is None):
			return
		self.clipboard.push(selectedText)
		self.model.deleteBefore()
		

	def pasteText(self, event=None):
		if(self.clipboard.isEmpty()):
			return
		text = self.clipboard.top()
		self.model.insert(text)

	def pasteTextAndPop(self, event=None):
		if(self.clipboard.isEmpty()):
			return
		text = self.clipboard.pop()
		self.model.insert(text)

	def undo(self, event=None):
		UndoManager.instance().undo()

	def redo(self, event=None):
		UndoManager.instance().redo()

	def openFile(self):
		file = fd.askopenfile()
		if file is None:
			return
		text = ''
		for line in file:
			text = text + line
		self.model = TextEditorModel.TextEditorModel(text)
		self.model.subscribeCursorObserver(self)
		self.model.subscribeTextObserver(self)		
		self.updateText()
		self.drawCursor()

	def saveFile(self):
		file = fd.asksaveasfile(mode='w', defaultextension='.txt')
		if file is None:
			return
		for l in self.model.allLines():
			file.write(l + '\n')
		file.close()

	def clearDocument(self):
		self.model.clearDocument()
	
	def cursorToStart(self):
		self.model.cursorToStart()
	
	def cursorToEnd(self):
		self.model.cursorToEnd()
	
	def updateStatusBar(self):
		x, y = self.model.cursorLocation.get()
		lineNum = len(self.model.lines)
		self.statusbar['text'] = 'Line ' + str(y + 1) + ', Column ' + str(x + 1) +', Lines: ' + str(lineNum)

	def loadPlugins(self):
		for m in os.listdir('plugins'):
			name, ext = os.path.splitext(m)
			if(ext == '.py'):
				module = importlib.import_module('plugins.' + name)
				p = getattr(module, name)()
				self.plugins.append(p)
		
	def executePlugin(self, plugin):
		plugin.execute(self.model, UndoManager.instance(), self.clipboard)



