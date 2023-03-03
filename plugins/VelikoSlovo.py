class VelikoSlovo:
	def getName(self):
		return 'VelikoSlovo'
	def getDescription(self):
		'Capitalizes every letter in a word'
	def execute(self, model, undoManager, clipboardStack):
		for i in range(len(model.lines)):
			print(model.lines[i])
			beginning = True
			spaceBefore = False
			for j in range(len(model.lines[i])):				
				if(beginning and model.lines[i][j] != ' '):
					model.lines[i] = model.lines[i][0:j] + model.lines[i][j].upper() + model.lines[i][j + 1:]
					beginning = False
				elif(model.lines[i][j] == ' '):
					spaceBefore = True
				elif(spaceBefore and model.lines[i][j] != ' '):
					model.lines[i] = model.lines[i][0:j] + model.lines[i][j].upper() + model.lines[i][j + 1:]
					spaceBefore = False
				else:
					spaceBefore = False
		model.notifyTextObservers()
		model.notifyCursorObservers()