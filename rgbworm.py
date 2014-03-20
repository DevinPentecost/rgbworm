"""
rgbworm.py
Helps with drawing
"""

#Imports
from Tkinter import *
import math, random, sys

class RGBWorm:
	
	#Initialization
	def __init__(self):
		
		#Set defaults
		
		#Pixel size
		self.pixelWidth = 3
		self.pixelHeight = 3
		
		#Color steps
		self.redMin = 100
		self.redMax = 255
		self.redStep = 5
		
		self.greenMin = 100
		self.greenMax = 255
		self.greenStep = 5
		
		self.blueMin = 100
		self.blueMax = 255
		self.blueStep = 5
		
		#Lookup lists
		self.usedPixels = []
		self.usedColors = []
		
		#What seed to use
		self.randomSeed = None
		self.random = None
	   
	"""
	setup
	Sets the drawing object up with the values specified
	""" 
	def setup(self):
	
		#Initialize the random seed
		if self.randomSeed is None:
			self.randomSeed = random.randrange(0, sys.maxint)
		self.random = random.Random(self.randomSeed)
		print "Setup with Random Seed: " + str(self.randomSeed)
		
		#Total number for each color
		self.redTotal = (self.redMax - self.redMin)/self.redStep
		self.greenTotal = (self.greenMax - self.greenMin)/self.greenStep
		self.blueTotal = (self.blueMax - self.blueMin)/self.blueStep
		
		#Figure out the number of pixels to make
		self.totalPixels = self.redTotal * self.greenTotal * self.blueTotal
							
		#Find the best square to hold them I guess
		self.canvasSize = int(math.sqrt(self.totalPixels * (self.pixelHeight * self.pixelWidth)))
		
		#Set up the canvas
		master = Tk()
		self.screen = Canvas(master, width = self.canvasSize, height = self.canvasSize, bg = 'white')
		self.screen.pack()
		
		#Generate the lookup arrays for used pixels
		#For each possible X coordinate...
		for x in range(0, self.canvasSize):
		
			#Make a list Y coordinates 'tall'
			l = [0]*self.canvasSize
			
			#And add it
			self.usedPixels.append(l)
			
		#Generate the lookup arrays for used color
		#For each possible Red...
		for r in range(0, self.redTotal):
		
			#Make a 'green' list
			gl = []
		
			#For each possible Green...
			for g in range(0, self.greenTotal):
				
				#Make a list B colors'tall'
				bl = [0]*self.blueTotal
				#And add it to green
				gl.append(bl)
			
			#Append this GREENxBLUE list
			self.usedColors.append(gl)
				
		
	"""
	shuffle(l)
	Shuffles a list and returns it
	"""
	def shuffle(self, l):
		self.random.shuffle(l)
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
		
		#Build the hex string
		color = '#%02X%02X%02X' % (r, g, b)
		
		#Draw the rect
		self.screen.create_rectangle(x, y, x + self.pixelWidth, y + self.pixelHeight, fill = color, width = 0)
		
		#Render the canvas
		self.screen.update()
		
	"""
	colorUsed
	Checks to see if a color has been used already
	"""
	def colorUsed(self, color):
	
		#Get the values
		(r, g, b) = color
		
		#Since colors are 'steps' out of the range, we have to figure out which step we are
		r = (r - self.redMin)/self.redStep - 1
		g = (g - self.greenMin)/self.greenStep - 1
		b = (b - self.blueMin)/self.blueStep - 1

		#Check to see if it used
		return self.usedColors[r][g][b] is 1
		
	"""
	useColor
	Sets the color as 'used'
	"""
	def useColor(self, color):
	
		#Get the values
		(r, g, b) = color

		#Since colors are 'steps' out of the range, we have to figure out which step we are
		r = (r - self.redMin)/self.redStep - 1
		g = (g - self.greenMin)/self.greenStep - 1
		b = (b - self.blueMin)/self.blueStep - 1
		
		#Simply set it to 1
		self.usedColors[r][g][b] = 1
		
	"""
	pixelUsed
	Checks to see if a particular pixel has already been selected
	"""
	def pixelUsed(self, pixel):
		
		#Get the values
		(x, y) = pixel
	
		#Check to see if it is 'used' as 1
		return self.usedPixels[x][y] is 1
		
	"""
	usePixel
	Sets the pixel as 'used'
	"""
	def usePixel(self, pixel):
	
		#Get the values
		(x, y) = pixel
	
		#Simply set it to 1, or 'used'
		self.usedPixels[x][y] = 1
		
		
	"""
	renderWorm
	Do all the hard work moving a worm around
	"""
	def renderWorm(self):
		
		#Randomly generate the starting color
		startRed = self.random.randrange(self.redMin, self.redMax, self.redStep)
		startGreen = self.random.randrange(self.greenMin, self.greenMax, self.greenStep)
		startBlue = self.random.randrange(self.blueMin, self.blueMax, self.blueStep)
		
		#Start at the origin
		startX = self.canvasSize/2
		startY = self.canvasSize/2
		
		#All the active pixels. Start with the middle one
		self.currentPixels = [(startX, startY)]
		self.currentColors = [(startRed, startGreen, startBlue)]
		
		#'Use' the first pixel
		self.usePixel((startX, startY))
		self.useColor((startRed, startGreen, startBlue))
		
		#While we still have active pixels
		while self.currentPixels:
			
			#Get the pixel
			currentPixel = self.currentPixels.pop()
			currentColor = self.currentColors.pop()


			#Tell us!
			#print "Drawing pixel at location: ", currentPixel[0], currentPixel[1], "with color: ", currentColor[0], currentColor[1], currentColor[2]
			
			#Draw it
			self.drawSquare(currentPixel[0], currentPixel[1], currentColor[0], currentColor[1], currentColor[2])
			
			#Add it to the used pixels
			self.usePixel(currentPixel)
				
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
							
						#Is the color outside of min/max ranges?
						if 	r < self.redMin or r > self.redMax or \
							g < self.greenMin or g > self.greenMax or \
							b < self.blueMin or b > self.blueMax:
							continue
						
						if not self.colorUsed((r, g, b)):
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
					if self.pixelUsed((pixelX, pixelY)):

						#Also ignore it
						continue
					
					#Randomly pick one for the neighbor color if there is one. Otherwise WHO KNOWS
					if possibleColors:
						
						#Pick the color
						index = self.random.randrange(len(possibleColors))
						newColor = possibleColors[index]
						
						#Remove from possible colors
						possibleColors.remove(newColor)
						self.currentColors.append(newColor)
						
						#Add this pixel to the draw queue
						self.currentPixels.append((pixelX, pixelY))
						
						#Say we've already selected this color
						self.useColor(newColor)
						
						#Also add this pixel
						self.usePixel((pixelX, pixelY))
		
#Default running from command line
if __name__ == '__main__':
	#Build it and run it
	worm = RGBWorm()
	worm.randomSeed = 1448864733
	worm.setup()
	worm.renderWorm()
	
	#Wait for enter before we kill it
	input("Render Complete!\nPress Enter to quit...\n")

