"""
RGBWorm GUI
A Gui for the RGB worm!
"""

"""Imports"""
from Tkinter import *
import rgbworm

class RGBWormGUI:

	"""
	__init__
	Initializes and creates everything for the GUI
	"""
	def __init__(self):	
	
		#Misc vars
		labelCol = 0
		entryCol = 1
	
		#Set up the gui...
		self.root = Tk()
		
		#Create an options frame
		optionFrame = Frame(self.root)
		
		######################################################################
		#Set up the canvas size percent
		sizeLabel = Label(self.root, text = "Canvas Size Percentage")
		sizeEntry = Entry(self.root, bd = 4, width = 4)
		sizeEntry.insert(0,'100')
		sizeLabel.grid(row = 0, column = labelCol)
		sizeEntry.grid(row = 0, column = entryCol + 1)
		######################################################################
		
		######################################################################
		#Set up the color options
		redLabel = Label(self.root, text = "Red Start/End/Step")
		redEntryStart = Entry(self.root, bd = 4, width = 4)
		redEntryStart.insert(0,'0')
		redEntryEnd = Entry(self.root, bd = 4, width = 4)
		redEntryEnd.insert(0,'255')
		redEntryStep = Entry(self.root, bd = 4, width = 4)
		redEntryStep.insert(0,'5')
		redLabel.grid(		row = 1, column = labelCol)
		redEntryStart.grid(	row = 1, column = entryCol)
		redEntryEnd.grid(	row = 1, column = entryCol+1)
		redEntryStep.grid(	row = 1, column = entryCol+2)
		
		greenLabel = Label(self.root, text = "Green Start/End/Step")
		greenEntryStart = Entry(self.root, bd = 4, width = 4)
		greenEntryStart.insert(0,'0')
		greenEntryEnd = Entry(self.root, bd = 4, width = 4)
		greenEntryEnd.insert(0,'255')
		greenEntryStep = Entry(self.root, bd = 4, width = 4)
		greenEntryStep.insert(0,'5')		
		greenLabel.grid(		row = 2, column = labelCol)
		greenEntryStart.grid(	row = 2, column = entryCol)
		greenEntryEnd.grid(		row = 2, column = entryCol+1)
		greenEntryStep.grid(	row = 2, column = entryCol+2)
		
		blueLabel = Label(self.root, text = "Blue Start/End/Step")
		blueEntryStart.insert(0,'0')
		blueEntryEnd = Entry(self.root, bd = 4, width = 4)
		blueEntryEnd.insert(0,'255')
		blueEntryStep = Entry(self.root, bd = 4, width = 4)
		blueEntryStep.insert(0,'5')	
		blueLabel.grid(			row = 3, column = labelCol)
		blueEntryStart.grid(	row = 3, column = entryCol)
		blueEntryEnd.grid(		row = 3, column = entryCol+1)
		blueEntryStep.grid(		row = 3, column = entryCol+2)
		######################################################################
		
		######################################################################
		#Set up possible render modes
		renderVar = IntVar()
		wormRadio = RadioButton(self.root, text = 'Worm', variable = renderVar, value = 'WORM')
		randomRadio = RadioButton(self.root, text = 'Random', variable = renderVar, value = 'RANDOM')
		bloomRadio = RadioButton(self.root, text = 'Bloom', variable = renderVar, value = 'BLOOM')
		
		
		