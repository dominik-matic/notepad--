from ClipboardObserver import ClipboardObserver

class ClipboardStack:
	def __init__(self):
		self.texts = []
		self.observers = []

	def push(self, text: str):
		self.texts.append(text)
		self.notifyObservers()
	
	def pop(self):
		ret = self.texts.pop()
		self.notifyObservers()
		return ret

	def top(self):
		return self.texts[-1]
	
	def isEmpty(self):
		return True if len(self.texts) == 0 else False

	def clear(self):
		self.texts.clear()

	def subscribe(self, obs: ClipboardObserver):
		self.observers.append(obs)
	
	def unsubscribe(self, obs: ClipboardObserver):
		self.observers.remove(obs)
	
	def notifyObservers(self):
		for obs in self.observers:
			obs.updateClipboard()
