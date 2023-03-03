from EditAction import EditAction

class UndoManager:
	_instance = None
	
	@staticmethod
	def instance(): 
		if (UndoManager._instance == None):
			UndoManager()
		return UndoManager._instance

	def __init__(self):
		if(UndoManager._instance is not None):
			raise Exception('UndoManager is a singleton')
		self.undoStack = []
		self.redoStack = []
		self.observers = []
		UndoManager._instance = self
	
	def undo(self):
		if(len(self.undoStack) == 0):
			return
		action = self.undoStack.pop()
		self.redoStack.append(action)
		action.execute_undo()
		self.notifyObservers()

	def redo(self):
		if(len(self.redoStack) == 0):
			return
		action = self.redoStack.pop()
		self.undoStack.append(action)
		action.execute_do()
		self.notifyObservers()

	def push(self, c: EditAction):
		self.redoStack.clear()
		self.undoStack.append(c)
		self.notifyObservers()

	def subscribe(self, obs):
		self.observers.append(obs)

	def unsubscribe(self, obs):
		self.observers.remove(obs)
		
	def notifyObservers(self):
		for obs in self.observers:
			obs.update(self.undoStackEmpty(), self.redoStackEmpty())

	def undoStackEmpty(self):
		return len(self.undoStack) == 0

	def redoStackEmpty(self):
		return len(self.redoStack) == 0