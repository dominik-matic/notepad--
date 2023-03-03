import tkinter as tk
from UndoObserver import UndoObserver
from ClipboardObserver import ClipboardObserver
from TextObserver import TextObserver
from UndoManager import UndoManager


class MenuBar(tk.Menu, UndoObserver, ClipboardObserver, TextObserver):

	def __init__(self, parent, plugins):
		tk.Menu.__init__(self, parent, relief=tk.FLAT)
		self.parent = parent
		self.plugins = plugins
		self.clipboard = self.parent.clipboard
		self.clipboard.subscribe(self)
		self.parent.model.subscribeTextObserver(self)
		UndoManager.instance().subscribe(self)
		self.initMenuBar()


	def initMenuBar(self):
		self.filemenu = tk.Menu(self, tearoff=0)
		self.filemenu.add_command(label='Open', command=self.parent.openFile)
		self.filemenu.add_command(label='Save', command=self.parent.saveFile)
		self.filemenu.add_separator()
		self.filemenu.add_command(label='Exit', command=self.parent.quit)

		self.editmenu = tk.Menu(self, tearoff=0)
		self.editmenu.add_command(label='Undo', command=self.parent.undo, state=tk.DISABLED)
		self.editmenu.add_command(label='Redo', command=self.parent.redo, state=tk.DISABLED)
		self.editmenu.add_separator()
		self.editmenu.add_command(label='Cut', command=self.parent.cutText, state=tk.DISABLED)
		self.editmenu.add_command(label='Copy', command=self.parent.copyText, state=tk.DISABLED)
		self.editmenu.add_command(label='Paste', command=self.parent.pasteText, state=tk.DISABLED)
		self.editmenu.add_command(label='Pate and Take', command=self.parent.pasteTextAndPop, state=tk.DISABLED)
		self.editmenu.add_separator()
		self.editmenu.add_command(label='Delete selection', command=self.parent.model.deleteBefore, state=tk.DISABLED)
		self.editmenu.add_command(label='Clear document', command=self.parent.clearDocument)

		self.movemenu = tk.Menu(self, tearoff=0)
		self.movemenu.add_command(label='Cursor to document start', command=self.parent.cursorToStart)
		self.movemenu.add_command(label='Cursor to document end', command=self.parent.cursorToEnd)
		
		self.add_cascade(label='File', menu=self.filemenu)
		self.add_cascade(label='Edit', menu=self.editmenu)
		self.add_cascade(label='Move', menu=self.movemenu)

		if(len(self.plugins) != 0):
			self.addPluginMenu()

		toolbar = tk.Frame(self.parent, bd=1, relief=tk.FLAT)

		self.undoBtn = tk.Button(toolbar, text='Undo', command=self.parent.undo, state=tk.DISABLED, relief=tk.FLAT)
		self.redoBtn = tk.Button(toolbar, text='Redo', command=self.parent.redo, state=tk.DISABLED, relief=tk.FLAT)
		self.cutBtn = tk.Button(toolbar, text='Cut', command=self.parent.cutText, state=tk.DISABLED, relief=tk.FLAT)
		self.copyBtn = tk.Button(toolbar, text='Copy', command=self.parent.copyText, state=tk.DISABLED, relief=tk.FLAT)
		self.pasteBtn = tk.Button(toolbar, text='Paste', command=self.parent.pasteText, state=tk.DISABLED, relief=tk.FLAT)
		
		self.undoBtn.pack(side=tk.LEFT, padx=2, pady=2)
		self.redoBtn.pack(side=tk.LEFT, padx=2, pady=2)
		self.cutBtn.pack(side=tk.LEFT, padx=2, pady=2)
		self.copyBtn.pack(side=tk.LEFT, padx=2, pady=2)
		self.pasteBtn.pack(side=tk.LEFT, padx=2, pady=2)
		
		toolbar.pack(side=tk.TOP, fill=tk.X)
		
		

	def addPluginMenu(self):
		self.pluginMenu = tk.Menu(self, tearoff=0)
		for p in self.plugins:
			self.pluginMenu.add_command(label=p.getName(), command=lambda: self.parent.executePlugin(p))
		self.add_cascade(label='Plugins', menu=self.pluginMenu)

	def updateClipboard(self):
		if(self.clipboard.isEmpty()):
			self.pasteBtn['state'] = tk.DISABLED
			self.editmenu.entryconfig(5, state=tk.DISABLED)
			self.editmenu.entryconfig(6, state=tk.DISABLED)
		else:
			self.pasteBtn['state'] = tk.NORMAL
			self.editmenu.entryconfig(5, state=tk.NORMAL)
			self.editmenu.entryconfig(6, state=tk.NORMAL)

	def update(self, undoIsEmpty, redoIsEmpty):	
		if(undoIsEmpty):
			self.undoBtn['state'] = tk.DISABLED
			self.editmenu.entryconfig(0, state=tk.DISABLED)
		else:
			self.undoBtn['state'] = tk.NORMAL
			self.editmenu.entryconfig(0, state=tk.NORMAL)
		if(redoIsEmpty):
			self.redoBtn['state'] = tk.DISABLED
			self.editmenu.entryconfig(1, state=tk.DISABLED)
		else:
			self.redoBtn['state'] = tk.NORMAL
			self.editmenu.entryconfig(1, state=tk.NORMAL)

	def updateText(self):
		if(self.parent.model.selectionRange is None):
			self.cutBtn['state'] = tk.DISABLED
			self.copyBtn['state'] = tk.DISABLED

			self.editmenu.entryconfig(3, state=tk.DISABLED)
			self.editmenu.entryconfig(4, state=tk.DISABLED)
			self.editmenu.entryconfig(8, state=tk.DISABLED)
			
		else:
			self.cutBtn['state'] = tk.NORMAL
			self.copyBtn['state'] = tk.NORMAL

			self.editmenu.entryconfig(3, state=tk.NORMAL)
			self.editmenu.entryconfig(4, state=tk.NORMAL)
			self.editmenu.entryconfig(8, state=tk.NORMAL)
			
