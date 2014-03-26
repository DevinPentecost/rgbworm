"""
rgbworm.py
Helps with drawing
"""

#Imports
from Tkinter import *
import math, random, sys
import time
from timer import Timer
import Image, ImageDraw

class RGBWorm:

	RENDERTYPES = ['WORM', 'RANDOM', 'BLOOM']
	
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
		
		self.greenMin = 0
		self.greenMax = 125
		self.greenStep = 1
		
		self.blueMin = 0
		self.blueMax = 125
		self.blueStep = 1
		
		#Lookup lists
		self.usedPixels = []
		self.usedColors = []
		
		#What seed to use
		self.randomSeed = None
		self.random = None
		
		#Canvas size reduction percentage, do help reduce whitespace
		self.canvasPercent = 100.0
		
		#How many 'worms' to run at any time
		#Running multiple worms creates a 'wider' worm
		self.simultaneousWorms = 1
		
		#Render using WORM by default
		self.renderType = 'WORM'
		
		#Update rate, once every X draws
		self.renderRate = 1
		
		#Force the canvas to be a particular size
		self.forceCanvasSize = False
		
		#For masking when rendering the output
		self.maskPath = None
		self.drawMask = False
		self.maskIgnore = (255, 255, 255, 255)
		
		(self.startX, self.startY) = (None, None)
		(self.startRed, self.startGreen, self.startBlue) = (None, None, None)
	   
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
		print "Canvas Percent at " + str(self.canvasPercent) + '%'
		
		#Total number for each color
		self.redTotal = (self.redMax - self.redMin)/self.redStep
		self.greenTotal = (self.greenMax - self.greenMin)/self.greenStep
		self.blueTotal = (self.blueMax - self.blueMin)/self.blueStep
		
		#Figure out the number of pixels to make
		self.totalColors = (self.redTotal * self.greenTotal * self.blueTotal)
		
		#Find the best square to hold them I guess
		self.canvasSize = int(math.sqrt(self.totalColors * (self.pixelHeight * self.pixelWidth)) * float(self.canvasPercent/100.0))
		
		
		#Do we want to use a pre defined size?
		if not self.forceCanvasSize or (self.canvasHeight in [None, 0]) or (self.canvasWidth in [None, 0]):
			self.canvasHeight = self.canvasWidth = self.canvasSize
		print "Canvas Resolution at " + str(self.canvasWidth) + 'x' + str(self.canvasHeight)
		
		
		#The total pixel count
		self.totalPixels = (self.canvasWidth * self.canvasHeight) / (self.pixelWidth * self.pixelHeight)
		
		#Set up the canvas
		master = Tk()
		self.screen = Canvas(master, width = self.canvasWidth, height = self.canvasHeight, bg = 'white')
		self.screen.pack()
		
		#Generate the lookup arrays for used pixels
		#For each possible X coordinate...
		self.usedPixels = []
		for x in range(0, self.canvasWidth):
		
			#Make a list Y coordinates 'tall'
			l = [0]*self.canvasHeight
			
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
		
		#Image for outputting
		self.image = Image.new("RGB", (self.canvasWidth, self.canvasHeight), '#FFFFFF')
		self.draw = ImageDraw.Draw(self.image)
		
		#Timers for tracking various areas of code
		self.timers = {
			"RENDER": [],
			"MULTIPLEPIXELS": [],
			"RENDERPIXEL": [],
			"GETPIXELCOLOR": [],
			"ADDPIXELCOLOR": [],
			"DRAWPIXEL": [],
		}
		
		#Randomly generate the starting color if there is none already
		if None in (self.startRed, self.startGreen, self.startBlue):
			self.startRed = self.random.randrange(self.redMin, self.redMax, self.redStep)
			self.startGreen = self.random.randrange(self.greenMin, self.greenMax, self.greenStep)
			self.startBlue = self.random.randrange(self.blueMin, self.blueMax, self.blueStep)
		
		#Start at the origin unless otherwise specified
		if None in (self.startX, self.startY):
			self.startX = self.canvasWidth/2
			self.startY = self.canvasHeight/2
		
		#Do we want to preload an image?
		if self.maskPath is not None:
			#Load the image and preset all the pixels
			self.applyMask(self.maskPath)
			
			#Do we want to draw the mask as well?
			if self.drawMask:
				#Not yet
				print "Not drawing mask"
	
	
	"""
	applyMask
	Loads a file and applies it as a mask to the image
	"""
	#@profile
	def applyMask(self, maskPath):
	
		#Print!
		print "Attempting to apply mask: ", maskPath
		
		#Load the mask and see if it matches the image size
		image = Image.open(maskPath)
		mask = image.load()
		
		#Out of bounds?
		if self.canvasWidth != image.size[0] or self.canvasHeight != image.size[1]:
			#Abort!
			print "Image size: ", (self.canvasWidth, self.canvasHeight), "does not match mask size: ", image.size
		
		else:		
			#We go through each pixel and see if it isn't the mask color
			for x in range(self.canvasWidth):
				for y in range(self.canvasHeight):
					#Check the color!
					if mask[x, y] != self.maskIgnore:
						#Set that pixel to be taken!
						#print 'FOUND', x, y, mask[x, y]
						self.usedPixels[x][y] = 1
						
		#Done
		print "Done applying mask"
	
		
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
	saveImage
	Saves the image to a path
	"""
	def saveImage(self, path):
		#Just save it
		self.image.save(path)
		
	"""
	drawSquare(x, y, color)
	Draws a square at the X/Y location (top left of the square), of a height/width and of a color
	"""
	#@profile
	def drawSquare(self, x, y, r, g, b):
		
		#Time drawing
		with Timer() as t:
		
			#Build the hex string
			color = '#%02X%02X%02X' % (r, g, b)
			
			#Draw the rect, but only if we are actually rendering in real time
			if self.renderRate != 0:
				self.screen.create_rectangle(x, y, x + self.pixelWidth, y + self.pixelHeight, fill = color, width = 0)
			
			#Also draw to the image
			self.draw.rectangle( [x, y, x + self.pixelWidth, y + self.pixelHeight], fill = color)
			
			#Are we on a render cycle?
			if self.renderRate != 0 and self.pixelCount % self.renderRate == 0:
			
				#Render the canvas
				self.screen.update()
			
		#Save the time
		#self.timers['DRAWPIXEL'].append(t.secs)
		
	"""
	colorUsed
	Checks to see if a color has been used already
	"""
	#@profile
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
	#@profile
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
	#@profile
	def pixelUsed(self, pixel):
		
		#Get the values
		(x, y) = pixel
		
		#Check to see if it is 'used' as 1
		return self.usedPixels[x][y] is 1
		
	"""
	usePixel
	Sets the pixel as 'used'
	"""
	#@profile
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
	#@profile
	def getPixelsColors(self):
		
		#Time it
		with Timer() as t:
		
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
						index = self.random.randrange(0, len(self.currentPixelColors))
						
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
					
		#Save the time
		#self.timers['GETPIXELCOLOR'].append(t.secs)
		
		#Return the tuple
		return pixelColors
		
	"""
	addCurrentPixel
	Adds a 'current' pixel to the 'to be done' list
	"""
	#@profile
	def addCurrentPixelColor(self, pixelColor):
		
		#Time it
		with Timer() as t:
		
			#What we do will depend on the operating mode
			
			#Random or worm?
			if self.renderType in ('WORM', 'RANDOM'):
				
				#Just add them to the end
				self.currentPixelColors.append(pixelColor)
				
			#Bloom?
			if self.renderType is 'BLOOM':
	
				#Queue it up for later
				self.bloomDelay.insert(0, pixelColor)
				
		#Save the time
		#self.timers['ADDPIXELCOLOR'].append(t.secs)
				
	"""
	renderWorm
	Do all the hard work moving a worm around
	"""
	#@profile
	def renderWorm(self):
		
		#We're starting!
		print "Beginning render..."
		
		#Start a timer...
		with Timer() as renderTimer:
			
			#All the active pixels. Start with the middle one
			self.currentPixelColors.append( ((self.startX, self.startY), (self.startRed, self.startGreen, self.startBlue)) )
			
			#'Use' the first pixel
			self.usePixel((self.startX, self.startY))
			self.useColor((self.startRed, self.startGreen, self.startBlue))
			
			#Set up some calls so there are less . notations. Should increase performance...
			currentPixelColors = self.currentPixelColors
			bloomDelay = self.bloomDelay
			getPixelsColors = self.getPixelsColors
			drawSquare = self.drawSquare
			shuffle = self.shuffle
			
			redStep = self.redStep
			greenStep = self.greenStep
			blueStep = self.blueStep
			redMin = self.redMin
			greenMin = self.greenMin
			blueMin = self.blueMin
			redMax = self.redMax
			greenMax = self.greenMax
			blueMax = self.blueMax
			
			colorUsed = self.colorUsed
			pixelUsed = self.pixelUsed
			
			pixelWidth = self.pixelWidth
			pixelHeight = self.pixelHeight
			
			canvasWidth = self.canvasWidth
			canvasHeight = self.canvasHeight
			
			random = self.random
			
			usePixel = self.usePixel
			useColor = self.useColor
			
			addCurrentPixelColor = self.addCurrentPixelColor
			
			timers = self.timers
			
			#While we still have active pixels
			while currentPixelColors or bloomDelay:
			
				#Time how long it takes to do this set of pixels
				with Timer() as multipleTimer:
			
					#We use a list of pixels to render this go around
					pixelColors = getPixelsColors()
					
					#Save a copy so we can append them onto the end
					pixelColorsDelay = []
					
					#Keep picking pixels/colors while we can...
					while pixelColors:
						
						#The time to do this individual render
						with Timer() as pixelTimer:
						
							#Get the pixel
							currentPixelColor = pixelColors.pop()
							
							#Get info from the pixel color tuple
							currentPixel = currentPixelColor[0]
							currentColor = currentPixelColor[1]
			
							#We haven't found a neighbor yet
							firstNeighbor = True
									
							#Draw it
							drawSquare(currentPixel[0], currentPixel[1], currentColor[0], currentColor[1], currentColor[2])
												
							#We want to assign these neighbors colors
							#Lets build all the possible colors that could be neighbors
							possibleColors = []
							for r in shuffle([-1, 0, 1]):
								for g in shuffle([-1, 0, 1]):
									for b in shuffle([-1, 0, 1]):
									
										#Is it the same color? One of the delayed ones?
										if (r is 0 and g is 0 and b is 0):
											#Dont use it
											continue
										
										#Add them to the possibilities
										r = ((redStep * r)) + currentColor[0]
										g = ((greenStep * g)) + currentColor[1]
										b = ((blueStep * b)) + currentColor[2]
										
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
										if 	r < redMin or r > redMax or \
											g < greenMin or g > greenMax or \
											b < blueMin or b > blueMax:
											continue
										
										if not colorUsed((r, g, b)):
											possibleColors.append((r, g, b))
								
							#Now we check all its neighbors
							for x in shuffle([-1, 0, 1]):
								for y in shuffle([-1, 0, 1]):
									
									#Is it the same pixel?
									if (x is 0 and y is 0):
										#Don't do ourselves again!
										continue
								
				
									#Go that far left or right, depending on the pixel size
									pixelX = currentPixel[0] + (x * pixelWidth)	
									pixelY = currentPixel[1] + (y * pixelHeight)
									
									#Is it one of the delayed ones? Don't do those again either
									pixelsDelay = [colorPixel[0] for colorPixel in pixelColorsDelay]
									if (pixelX, pixelY) in pixelsDelay:
										continue
									
									#Did we go off the edge?
									if 	pixelX < 0 or \
										pixelX >= canvasWidth or \
										pixelY < 0 or \
										pixelY >= canvasHeight:
										
										#Ignore this pixel
										continue
									
									#Do we already have this pixel?
									if pixelUsed((pixelX, pixelY)):
				
										#Also ignore it
										continue
									
									#Randomly pick one for the neighbor colors if there is one. Otherwise WHO KNOWS
									if possibleColors:
										
										#Pick the color and remove it
										index = random.randrange(len(possibleColors))
										newColor = possibleColors.pop(index)
										
										#Add it to the used pixels and colors
										usePixel((pixelX, pixelY))
										useColor(newColor)
										
										#If we are the first 'neighbor' of this pixel, we want to add it at the end!
										if firstNeighbor:
										
											#Don't use it again!
											firstNeighbor = False
											
											#Also push it to our delay
											pixelColorsDelay.append( ((pixelX, pixelY), newColor) )
											
										else:
											#Add it to the list of current pixels and colors immediately
											addCurrentPixelColor( ((pixelX, pixelY), newColor) )
											
						#Save the time it took for this one pixel
						#timers['RENDERPIXEL'].append(pixelTimer.secs)
									
					#The current set of pixels/colors need to be added onto the end
					while pixelColorsDelay:
						#Add these onto the end
						addCurrentPixelColor(pixelColorsDelay.pop())
					
				#Add this time
				#timers['MULTIPLEPIXELS'].append(multipleTimer.secs)
				
		#Done
		print "Done with Render."
		
		#Add the render time to the timers
		#timers['RENDER'].append(renderTimer.secs)

		
#Default running from command line
if __name__ == '__main__':
	#Build it and run it
	worm = RGBWorm()
	
	#worm.randomSeed = 368909920
	
	#For stats...
	maskPath = 'Masks/dota1080.png'
	
	canvasSizes = range(40, 50, 100)
	
	renderTypes = ['WORM', 'RANDOM', 'BLOOM']
	
	wormCounts = [1]
	
	startPositions = [(880, 650), (1080, 435), (600, 160), (1300, 850)]
	
	
	#Time each render as well as going through all type...
	for size in canvasSizes:
		for type in renderTypes:
			for count in wormCounts:
				for position in startPositions:
			
					startTime = time.time()
					
					worm.canvasPercent = float(size)
					worm.renderType = type
					worm.renderRate = 0
					worm.simultaneousWorms = count
					
					(worm.startX, worm.startY) = position
					(worm.startRed, worm.startGreen, worm.startBlue) = (200, 50, 50)
					
					worm.forceCanvasSize = True
					worm.canvasWidth = 1920
					worm.canvasHeight = 1080
					
					worm.maskPath = maskPath
					
					worm.setup()
					worm.renderWorm()
					endTime = time.time() - startTime
					
					#Print out the amount of colors used
					print 'Pixels used out of total: ', worm.pixelCount, worm.totalPixels, (float(worm.pixelCount)/float(worm.totalPixels))*100.0
					print 'Colors used out of total: ', worm.colorCount, worm.totalColors, (float(worm.colorCount)/float(worm.totalColors))*100.0
					print 'Exectution time: ', endTime, 's'
					
					#Wait for enter before we kill it
					path = './Images/' + str(time.time()) + '_' + str(worm.randomSeed) + '.png'
					print 'Saving Image to path: ' + str(path)
					worm.saveImage(path)
					#raw_input("Render Complete!\nPress Enter to continue...\n")
					#worm.clear()
	
	
	"""
	#Basic run
	worm.canvasPercent = 40.0
	worm.renderType = 'BLOOM'
	worm.setup()
	worm.renderWorm()
	worm.saveImage('./Images/' + str(time.time()) + '_' + str(worm.randomSeed) + '.png')
	"""
	
	#Completely done!
	#raw_input("Done with RGBWorm command line. Hit enter to quit...")
		
		
	
	
	
	

	
	

