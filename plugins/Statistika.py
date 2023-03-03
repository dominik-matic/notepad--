import tkinter as tk
from tkinter.messagebox import showinfo
import re

class Statistika:
	def getName(self):
		return 'Statistika'
	def getDescription(self):
		'Tells you how many lines, words and letters there are in a file'
	def execute(self, model, undoManager, clipboardStack):
		words = 0
		letters = 0
		text = model.lines
		ln = len(text)
		
		for line in text:
			letters = letters + len(line) # pretpostavljam da su razmaci letters
			words = words + len(re.findall(r'\w+', line))
		
		toShow = 'Lines: ' + str(ln) + '\nWords: ' + str(words) + '\nLetters: ' + str(letters)
		showinfo('Statistika', toShow)