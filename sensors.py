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

version = 0
newImages = 0	# Flag for if new images were taken (So "door closed" loop doesn't endlessly try to clear image folder)
newBatch = 0 	# New folder/batch of images

# Getting the current date and time
dt = datetime.now()

# getting the timestamp
# ts = datetime.timestamp(dt)
# print(str(dt))

# exten = os.path.join("/home/shamispi/Desktop/ece-140a-winter-2022-jcam306","tempPictures", str(dt))
exten = os.path.join("/home/shamispi/Desktop/","images")

if not os.path.exists(exten):
    os.mkdir(exten)

while True:

	if doorSensor.value:
		print("Door OPEN!")
		if newBatch == 1:		# Reset Date Time if new batch of images
			newBatch = 0
			dt = datetime.now()
		ret, image = camera.read() 
		# cv2.imwrite(("./tempPictures/" + str(dt) +"/sensorTest" + str(version) + ".jpg"), image) 
		cv2.imwrite(("/home/shamispi/Desktop/images/" + str(dt) + "_" + str(version) + ".jpg"), image) 
		version += 1
		newImages = 1
	elif (0 == doorSensor.value):
		print("DOOR CLOSED!")
		if newImages == 1:
			#call sender.py and send images
			sender.sendFolder(exten)
			for file in os.listdir(exten):				# Clear folder on images from previous image capture sequence
				os.remove(os.path.join(exten, file))
			newImages = 0								# Reset if new images to send
			newBatch = 1								# Reset for new batch of images
	else:
		print("Sensor NOT DETECTED")
		camera.release() 

	time.sleep(0.5)
	
camera.release() 