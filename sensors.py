import time
import board
import digitalio
import cv2

# set up door sensor
door_sensor = digitalio.DigitalInOut(board.D23)
door_sensor.direction = digitalio.Direction.INPUT
door_sensor.pull = digitalio.Pull.UP

camera = cv2.VideoCapture(0)    # Initialize the camera module

while True:

	if door_sensor.value:
		print("Sensor OFF!")
	elif (0 == door_sensor.value):
		print("Sensor ON!")
		ret, image = camera.read() 
		cv2.imwrite(("./sensorTest.jpg"), image) 
	else:
		print("Sensor NOT DETECTED")
		camera.release() 

	time.sleep(0.5)
	
camera.release() 
