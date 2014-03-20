"""
rgbworm.py
Helps with drawing
"""

#Imports
from Tkinter import *
import math, random, sys
import time

class RGBWorm:

	RENDERTYPES = ['WORM', 'RANDOM', 'BLOOM']
	
	#Initialization
	def __init__(self):
		
		#Set defaults
		
		#Pixel size
		self.pixelWidth = 1
		self.pixelHeight = 1
		
		#Color steps
		self.redMin = 0
		self.redMax = 255
		self.redStep = 5
		
		self.greenMin = 0
		self.greenMax = 255
		self.greenStep = 5
		
		self.blueMin = 0
		self.blueMax = 255
		self.blueStep = 5
		
		#Lookup lists
		self.usedPixels = []
		self.usedColors = []
		
		#What seed to use
		self.randomSeed = None
		self.random = None
		
		#Canvas size reduction percentage, do help reduce whitespace
		self.canvasSizeReduction = 100.0
		
		#How many 'worms' to run at any time
		#Running multiple worms creates a 'wider' worm
		self.simultaneousWorms = 1
		
		#Render using WORM by default
		self.renderType = 'WORM'
	   
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
		print "Canvas Size at " + str(self.canvasSizeReduction) + '%'
		
		#Total number for each color
		self.redTotal = (self.redMax - self.redMin)/self.redStep
		self.greenTotal = (self.greenMax - self.greenMin)/self.greenStep
		self.blueTotal = (self.blueMax - self.blueMin)/self.blueStep
		
		#Figure out the number of pixels to make
		self.totalColors = (self.redTotal * self.greenTotal * self.blueTotal)
							
		#Find the best square to hold them I guess
		self.canvasSize = int(math.sqrt(self.totalColors * (self.pixelHeight * self.pixelWidth)) * float(self.canvasSizeReduction/100.0))
		
		#The total pixel count
		self.totalPixels = (self.canvasSize * self.canvasSize) / (self.pixelWidth * self.pixelHeight)
		
		#Set up the canvas
		master = Tk()
		self.screen = Canvas(master, width = self.canvasSize, height = self.canvasSize, bg = 'white')
		self.screen.pack()
		
		#Generate the lookup arrays for used pixels
		#For each possible X coordinate...
		self.usedPixels = []
		for x in range(0, self.canvasSize):
		
			#Make a list Y coordinates 'tall'
			l = [0]*self.canvasSize
			
			#And add it
			self.usedPixels.append(l)
			
		#Generate the lookup arrays for used color
		#For each possible Red...
		self.usedColors = []
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
			
		#The count of pixels used
		self.pixelCount = 0	
			
		#The count of colors used
		self.colorCount = 0
		
		#Start with 0 pixels in the queue
		self.currentPixelColors = []
		
		#Delay list for bloom render
		self.bloomDelay = []
		
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
		self.screen.delete("all")
		
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
		
		#Increment the color counter
		self.colorCount += 1
		
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
		
		#Increment the pixel count
		self.pixelCount += 1
	
		#Simply set it to 1, or 'used'
		self.usedPixels[x][y] = 1
		
	"""
	getPixelsColors
	Returns a tuple of pixel/color lists to use this render round
	"""
	def getPixelsColors(self):
		
		#Depending on the operating mode, we get some pixel(s) and color(s)
		
		pixelColors = []
		
		#Get the requested number of worms...
		for i in range(0, self.simultaneousWorms):
		
			#Are we grabbing worm type?
			if self.renderType is 'WORM':

				#Are there enough?
				if self.currentPixelColors:
				
					#Pop them off and use
					pixelColors.append(self.currentPixelColors.pop())
		
			#What about RANDOM! RANDOM! RANDOM!
			if self.renderType is 'RANDOM':
			
				#Are there enough?
				if self.currentPixelColors:
					
					#Get an index...
					index = self.random.randrange(0, len(self.currentPixels))
					
					#Pop them off and use
					pixelColors.append(self.currentPixelColors.pop(index))
		
			#Bloom!
			#Start in the middle, try to expand out as uniformly as possible...
			if self.renderType is 'BLOOM':

				#Is there still one in the current pixels?
				if not self.currentPixelColors:

					#There aren't any left. Are there any left in the delay queue? Move them over!
					self.currentPixelColors =  self.bloomDelay
					
					#Are there any new ones?
					if self.currentPixelColors:

						#Pop it off and use it
						pixelColors.append(self.currentPixelColors.pop())
				
				else:

					#Pop it off and use it
					pixelColors.append(self.currentPixelColors.pop())
					

		
		#Return the tuple
		return pixelColors
		
	"""
	addCurrentPixel
	Adds a 'current' pixel to the 'to be done' list
	"""
	def addCurrentPixelColor(self, pixelColor):
		
		#What we do will depend on the operating mode
		
		#Random or worm?
		if self.renderType in ('WORM', 'RANDOM'):
			
			#Just add them to the end
			self.currentPixelColors.append(pixelColor)
			
		#Bloom?
		if self.renderType is 'BLOOM':

			#Queue it up for later
			self.bloomDelay.insert(0, pixelColor)
				
	"""
	renderWorm
	Do all the hard work moving a worm around
	"""
	def renderWorm(self):
		
		#We're starting!
		print "Beginning render..."
		
		#Randomly generate the starting color
		startRed = self.random.randrange(self.redMin, self.redMax, self.redStep)
		startGreen = self.random.randrange(self.greenMin, self.greenMax, self.greenStep)
		startBlue = self.random.randrange(self.blueMin, self.blueMax, self.blueStep)
		
		#Start at the origin
		startX = self.canvasSize/2
		startY = self.canvasSize/2
		
		#All the active pixels. Start with the middle one
		self.currentPixelColors.append( ((startX, startY), (startRed, startGreen, startBlue)) )
		
		#'Use' the first pixel
		self.usePixel((startX, startY))
		self.useColor((startRed, startGreen, startBlue))
		
		#While we still have active pixels
		while self.currentPixelColors or self.bloomDelay:
		
			#We use a list of pixels to render this go around
			pixelColors = self.getPixelsColors()
			
			#Save a copy so we can append them onto the end
			pixelColorsDelay = []
			
			#Keep picking pixels/colors while we can...
			while pixelColors:
				
				#Get the pixel
				currentPixelColor = pixelColors.pop()
				
				#Get info from the pixel color tuple
				currentPixel = currentPixelColor[0]
				currentColor = currentPixelColor[1]

				#We haven't found a neighbor yet
				firstNeighbor = True
						
				#Draw it
				self.drawSquare(currentPixel[0], currentPixel[1], currentColor[0], currentColor[1], currentColor[2])
									
				#We want to assign these neighbors colors
				#Lets build all the possible colors that could be neighbors
				possibleColors = []
				for r in self.shuffle([-1, 0, 1]):
					for g in self.shuffle([-1, 0, 1]):
						for b in self.shuffle([-1, 0, 1]):
						
							#Is it the same color? One of the delayed ones?
							if (r is 0 and g is 0 and b is 0):
								#Dont use it
								continue
							
							#Add them to the possibilities
							r = ((self.redStep * r)) + currentColor[0]
							g = ((self.greenStep * g)) + currentColor[1]
							b = ((self.blueStep * b)) + currentColor[2]
							
							#Is it one of the delayed ones? Don't do them either
							colorsDelay = [colorPixel[1] for colorPixel in pixelColorsDelay]
							if (r, g, b) in colorsDelay:
								continue
							
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
					
				#Now we check all its neighbors
				for x in self.shuffle([-1, 0, 1]):
					for y in self.shuffle([-1, 0, 1]):
						
						#Is it the same pixel?
						if (x is 0 and y is 0):
							#Don't do ourselves again!
							continue
					
	
						#Go that far left or right, depending on the pixel size
						pixelX = currentPixel[0] + (x * self.pixelWidth)	
						pixelY = currentPixel[1] + (y * self.pixelHeight)
						
						#Is it one of the delayed ones? Don't do those again either
						pixelsDelay = [colorPixel[0] for colorPixel in pixelColorsDelay]
						if (pixelX, pixelY) in pixelsDelay:
							continue
						
						#Did we go off the edge?
						if 	pixelX < 0 or \
							pixelX >= self.canvasSize or \
							pixelY < 0 or \
							pixelY >= self.canvasSize:
							
							#Ignore this pixel
							continue
						
						#Do we already have this pixel?
						if self.pixelUsed((pixelX, pixelY)):
	
							#Also ignore it
							continue
						
						#Randomly pick one for the neighbor colors if there is one. Otherwise WHO KNOWS
						if possibleColors:
							
							#Pick the color and remove it
							index = self.random.randrange(len(possibleColors))
							newColor = possibleColors.pop(index)
							
							#Add it to the used pixels and colors
							self.usePixel((pixelX, pixelY))
							self.useColor(newColor)
							
							#If we are the first 'neighbor' of this pixel, we want to add it at the end!
							if firstNeighbor:
							
								#Don't use it again!
								firstNeighbor = False
								
								#Also push it to our delay
								pixelColorsDelay.append( ((pixelX, pixelY), newColor) )
								
							else:
								#Add it to the list of current pixels and colors immediately
								self.addCurrentPixelColor( ((pixelX, pixelY), newColor) )						
							
							
			#The current set of pixels/colors need to be added onto the end
			while pixelColorsDelay:
				#Add these onto the end
				self.addCurrentPixelColor(pixelColorsDelay.pop())
				
		#Done
		print "Done with Render."

		
#Default running from command line
if __name__ == '__main__':
	#Build it and run it
	worm = RGBWorm()
	
	worm.randomSeed = 368909920
	
	#For stats...
	canvasSizes = range(40, 100, 20)
	
	renderTypes = ['WORM', 'RANDOM']
	
	wormCounts = [1, 2, 3, 4, 5, 6]
	
	"""
	#Time each render as well as going through all type...
	for size in canvasSizes:
		for type in renderTypes:
			for count in wormCounts:
		
				startTime = time.time()
				
				worm.canvasSizeReduction = float(size)
				worm.renderType = type
				worm.simultaneousWorms = count
				
				worm.setup()
				worm.renderWorm()
				endTime = time.time() - startTime
				
				#Print out the amount of colors used
				print 'Pixels used out of total: ', worm.pixelCount, worm.totalPixels, (float(worm.pixelCount)/float(worm.totalPixels))*100.0
				print 'Colors used out of total: ', worm.colorCount, worm.totalColors, (float(worm.colorCount)/float(worm.totalColors))*100.0
				print 'Exectution time: ', endTime, 's'
				
				#Wait for enter before we kill it
				#raw_input("Render Complete!\nPress Enter to continue...\n")
				#worm.clear()
	"""
	
	#Basic run
	worm.canvasSizeReduction = 100.0
	worm.renderType = 'BLOOM'
	worm.setup()
	worm.renderWorm()
		
	#Completely done!
	raw_input("Done with RGBWorm command line. Hit enter to quit...")
		
		
	
	
	
	

	
	

