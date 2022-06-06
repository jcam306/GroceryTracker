import time
import board
import digitalio
import cv2
import os
from datetime import datetime
import sender

# set up door sensor
doorSensor = digitalio.DigitalInOut(board.D23)
doorSensor.direction = digitalio.Direction.INPUT
doorSensor.pull = digitalio.Pull.UP

camera = cv2.VideoCapture(0)    # Initialize the camera module

version    = 0	# Version number to differentiate images from each other within batches
versionSet = 0	# Version set number for efficient sorting
newImages  = 0	# Flag for if new images were taken (So "door closed" loop doesn't endlessly try to clear image folder)
newBatch   = 0 	# New batch of images

# Getting the current date and time
dt = datetime.now()

# exten = os.path.join("/home/shamispi/Desktop/ece-140a-winter-2022-jcam306","tempPictures", str(dt))
exten = os.path.join("/home/shamispi/Desktop/","images")

if not os.path.exists(exten):
    os.mkdir(exten)

while True:

	if doorSensor.value:
		print("Door OPEN!")
		if newBatch == 1:		# Reset Date Time if new batch of images
			dt = datetime.now()
			newBatch = 0
		ret, image = camera.read() 
		cv2.imwrite(("/home/shamispi/Desktop/images/" + str(dt) + "_" + str(versionSet) + str(version) + ".jpg"), image) 
		if version == 9:
			version = 0
			versionSet += 1
		else:
			version += 1
		newImages = 1
	elif (0 == doorSensor.value):
		print("DOOR CLOSED!")
		if newImages == 1:
			sender.sendFolder(exten)					# Send images folder to server
			for file in os.listdir(exten):				# Clear "images" folder from previous batch of images
				os.remove(os.path.join(exten, file))
			newImages  = 0								# Reset newImages flag 
			newBatch   = 1								# Reset new batch of images flag
			version    = 0								# Reset version number for new batch
			versionSet = 0								# Reset version set number for new batch
	else:
		print("Sensor NOT DETECTED")
		camera.release() 

	time.sleep(0.25)