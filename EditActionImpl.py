import copy
from EditAction import EditAction
from Location import Location
from LocationRange import LocationRange

class DeleteEditAction(EditAction):
	def __init__(self, model, start: Location, end: Location, text, cursorLoc):
		self.model = model
		self.start = copy.deepcopy(start)
		self.end = copy.deepcopy(end)
		self.text = text
		self.cursorLoc = cursorLoc
	def execute_do(self):
		self.model.setSelectionRange(LocationRange(copy.deepcopy(self.start), copy.deepcopy(self.end)))
		self.model.deleteRange(self.model.selectionRange)
		self.model.notifyTextObservers()
		self.model.notifyCursorObservers()

	def execute_undo(self):
		self.model.cursorLocation = copy.deepcopy(self.start)
		self.model.selectionRange = None
		self.model.insert(self.text, notify=False, invokeUM=False)
		if(self.cursorLoc == 'start'):
			self.model.cursorLocation = copy.deepcopy(self.start)
		self.model.notifyTextObservers()
		self.model.notifyCursorObservers()


class InsertEditAction(EditAction):
	def __init__(self, model, start: Location, end: Location, text):
		self.model = model
		self.start = copy.deepcopy(start)
		self.end = copy.deepcopy(end)
		self.text = text
	def execute_do(self):
		self.model.cursorLocation = copy.deepcopy(self.start)
		self.model.selectionRange = None
		self.model.insert(self.text, invokeUM=False)
	def execute_undo(self):
		self.model.setSelectionRange(LocationRange(copy.deepcopy(self.start), copy.deepcopy(self.end)))
		self.model.deleteRange(self.model.selectionRange)
		self.model.notifyTextObservers()
		self.model.notifyCursorObservers()