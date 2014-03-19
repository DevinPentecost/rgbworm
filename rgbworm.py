"""
rgbworm.py
Helps with drawing
"""

#Imports
from Tkinter import *
import math, random

class RGBWorm:
	
	#Initialization
	def __init__(self):
		
		#Set defaults
		
		#Pixel size
		self.pixelWidth = 1
		self.pixelHeight = 1
		
		#Color steps
		self.redMin = 100
		self.redMax = 255
		self.redStep = 1
		
		self.greenMin = 100
		self.greenMax = 255
		self.greenStep = 5
		
		self.blueMin = 100
		self.blueMax = 255
		self.blueStep = 5
	   
	"""
	setup
	Sets the drawing object up with the values specified
	""" 
	def setup(self):
		
		#Figure out the number of pixels to make
		self.totalPixels =  ((self.redMax - self.redMin)/self.redStep) * \
							((self.greenMax - self.greenMin)/self.greenStep) * \
							((self.blueMax - self.blueMin)/self.blueStep)
							
		#Find the best square to hold them I guess
		self.canvasSize = int(math.sqrt(self.totalPixels * (self.pixelHeight * self.pixelWidth)))
		
		#Set up the canvas
		master = Tk()
		self.screen = Canvas(master, width = self.canvasSize, height = self.canvasSize, bg = 'white')
		self.screen.pack()
		
	"""
	shuffle(l)
	Shuffles a list and returns it
	"""
	def shuffle(self, l):
		random.shuffle(l)
		return l
		
	"""
	clear
	Clears the screen canvas
	"""
	def clear(self):
		self.screen.clear()
		
	"""
	drawSquare(x, y, color)
	Draws a square at the X/Y location (top left of the square), of a height/width and of a color
	"""
	def drawSquare(self, x, y, r, g, b):
		
		#Build the color by shifting
		r = r
		g = g
		b = b
		
		#Build the hex string
		color = '#%02X%02X%02X' % (r, g, b)
		
		#Draw the rect
		self.screen.create_rectangle(x, y, x + self.pixelWidth, y + self.pixelHeight, fill = color, width = 0)
		
		#Render the canvas
		self.screen.update()
		
	"""
	renderWorm
	Do all the hard work moving a worm around
	"""
	def renderWorm(self):
		
		#Randomly generate the starting color
		startRed = random.randrange(self.redMin, self.redMax, self.redStep)
		startGreen = random.randrange(self.greenMin, self.greenMax, self.greenStep)
		startBlue = random.randrange(self.blueMin, self.blueMax, self.blueStep)
		
		#Start at the origin
		startX = self.canvasSize/2
		startY = self.canvasSize/2
		
		#All the currently used colors and pixels
		usedColors = [(startRed, startGreen, startBlue)]
		usedPixels = []
		
		#All the active pixels. Start with the middle one
		currentPixels = [(startX, startY)]
		currentColors = [(startRed, startGreen, startBlue)]
		
		#While we still have active pixels
		while currentPixels:
			
			#Get the pixel
			currentPixel = currentPixels.pop()
			currentColor = currentColors.pop()
			
			#Is it already rendered?
			if currentPixel not in usedPixels:
				
				#Tell us!
				#print "Drawing pixel at location: ", currentPixel[0], currentPixel[1], "with color: ", currentColor[0], currentColor[1], currentColor[2]
				
				#Draw it
				self.drawSquare(currentPixel[0], currentPixel[1], currentColor[0], currentColor[1], currentColor[2])
				
				#Add it to the used pixels
				usedPixels.append(currentPixel)
				
			#We want to assign these neighbors colors
			#Lets build all the possible colors that could be neighbors
			possibleColors = []
			for r in self.shuffle([-1, 0, 1]):
				for g in self.shuffle([-1, 0, 1]):
					for b in self.shuffle([-1, 0, 1]):
								
						#Add them to the possibilities
						r = ((self.redStep * r)) + currentColor[0]
						g = ((self.greenStep * g)) + currentColor[1]
						b = ((self.blueStep * b)) + currentColor[2]
						
						#Is the color out of range?
						if r < 0 or r > 255 or \
							g < 0 or g > 255 or \
							b < 0 or b > 255:
							continue
						
						if (r, g, b) not in usedColors:
							possibleColors.append((r, g, b))
							
			#print 'POSSIBLE COLORS:', possibleColors
				
			#Now we check all its neighbors
			for x in self.shuffle([-1, 0, 1]):
				for y in self.shuffle([-1, 0, 1]):
					
					#Go that far left or right, depending on the pixel size
					pixelX = currentPixel[0] + (x * self.pixelWidth)	
					pixelY = currentPixel[1] + (y * self.pixelHeight)
					
					#Did we go off the edge?
					if pixelX <= 0 or \
						pixelX > self.canvasSize or \
						pixelY <= 0 or \
						pixelY > self.canvasSize:
						
						#Ignore this pixel
						#print "We went off the edge"
						continue
					
					#Do we already have this pixel?
					if (pixelX, pixelY) in usedPixels:
						
						#Also ignore it
						continue
					
					#Randomly pick one for the neighbor color if there is one. Otherwise WHO KNOWS
					if possibleColors:
						
						#Pick the color
						index = random.randrange(len(possibleColors))
						newColor = possibleColors[index]
						
						#Remove from possible colors
						possibleColors.remove(newColor)
						currentColors.append(newColor)
						
						#Also add this pixel
						currentPixels.append((pixelX, pixelY))
						
		print 'DONE'
	
	"""
	renderRandom
	Pretty much the same as worm only its random, so not quite like worm.
	"""
	def renderRandom(self):
		
		#Randomly generate the starting color
		startRed = random.randrange(self.redMin, self.redMax, self.redStep)
		startGreen = random.randrange(self.greenMin, self.greenMax, self.greenStep)
		startBlue = random.randrange(self.blueMin, self.blueMax, self.blueStep)
		
		#Start at the origin
		startX = self.canvasSize/2
		startY = self.canvasSize/2
		
		#All the currently used colors and pixels
		usedColors = [(startRed, startGreen, startBlue)]
		usedPixels = []
		
		#All the active pixels. Start with the middle one
		currentPixels = [(startX, startY)]
		currentColors = [(startRed, startGreen, startBlue)]
		
		#While we still have active pixels
		while currentPixels:
			#Get a random index
			index = random.randrange(0, len(currentPixels))
			
			#Get the pixel
			currentPixel = currentPixels.pop(index)
			currentColor = currentColors.pop(index)
			
			#Is it already rendered?
			if currentPixel not in usedPixels:
				
				#Tell us!
				#print "Drawing pixel at location: ", currentPixel[0], currentPixel[1], "with color: ", currentColor[0], currentColor[1], currentColor[2]
				
				#Draw it
				self.drawSquare(currentPixel[0], currentPixel[1], currentColor[0], currentColor[1], currentColor[2])
				
				#Add it to the used pixels
				usedPixels.append(currentPixel)
				
			#We want to assign these neighbors colors
			#Lets build all the possible colors that could be neighbors
			possibleColors = []
			for r in self.shuffle([-1, 0, 1]):
				for g in self.shuffle([-1, 0, 1]):
					for b in self.shuffle([-1, 0, 1]):
								
						#Add them to the possibilities
						r = ((self.redStep * r)) + currentColor[0]
						g = ((self.greenStep * g)) + currentColor[1]
						b = ((self.blueStep * b)) + currentColor[2]
						
						#Is the color out of range?
						if r < 0 or r > 255 or \
							g < 0 or g > 255 or \
							b < 0 or b > 255:
							continue
						
						if (r, g, b) not in usedColors:
							possibleColors.append((r, g, b))
							
			#print 'POSSIBLE COLORS:', possibleColors
				
			#Now we check all its neighbors
			for x in self.shuffle([-1, 0, 1]):
				for y in self.shuffle([-1, 0, 1]):
					
					#Go that far left or right, depending on the pixel size
					pixelX = currentPixel[0] + (x * self.pixelWidth)	
					pixelY = currentPixel[1] + (y * self.pixelHeight)
					
					#Did we go off the edge?
					if pixelX <= 0 or \
						pixelX > self.canvasSize or \
						pixelY <= 0 or \
						pixelY > self.canvasSize:
						
						#Ignore this pixel
						#print "We went off the edge"
						continue
					
					#Do we already have this pixel?
					if (pixelX, pixelY) in usedPixels:
						
						#Also ignore it
						continue
					
					#Randomly pick one for the neighbor color if there is one. Otherwise WHO KNOWS
					if possibleColors:
						
						#Pick the color
						index = random.randrange(len(possibleColors))
						newColor = possibleColors[index]
						
						#Remove from possible colors
						possibleColors.remove(newColor)
						currentColors.append(newColor)
						
						#Also add this pixel
						currentPixels.append((pixelX, pixelY))
						
		print 'DONE'
		
#Default running from command line
if __name__ == '__main__':
	#Build it and run it
	worm = RGBWorm()
	worm.setup()
	worm.renderWorm()