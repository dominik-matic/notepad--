#!/bin/python
from TextEditor import TextEditor
from TextEditorModel import TextEditorModel

def main():
	tem = TextEditorModel('############################################################\n#                   Welcome to Notepad--                   #\n# Made by: Dominik Matić                                   #\n#                            The best programmer alive! :) #\n############################################################\n\n')
	te = TextEditor(tem)
	te.mainloop()

if __name__ == "__main__":
	main()