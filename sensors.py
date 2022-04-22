import time
import board
import digitalio
import cv2
import os
from datetime import datetime

# set up door sensor
doorSensor = digitalio.DigitalInOut(board.D23)
doorSensor.direction = digitalio.Direction.INPUT
doorSensor.pull = digitalio.Pull.UP

camera = cv2.VideoCapture(0)    # Initialize the camera module

version = 0

# Getting the current date and time
dt = datetime.now()
# getting the timestamp
# ts = datetime.timestamp(dt)
print(str(dt))

exten = os.path.join("/home/shamispi/Desktop/ece-140a-winter-2022-jcam306","tempPictures", str(dt))

if not os.path.exists(exten):
    os.mkdir(exten)

while True:

	if doorSensor.value:
		print("Door CLOSED!")
	elif (0 == doorSensor.value):
		print("DOOR OPEN!")
		ret, image = camera.read() 
		cv2.imwrite(("./tempPictures/" + str(dt) +"/sensorTest" + str(version) + ".jpg"), image) 
		version += 1
	else:
		print("Sensor NOT DETECTED")
		camera.release() 

	time.sleep(0.5)
	
camera.release() 