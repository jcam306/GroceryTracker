import requests
import os

def sendFolder(folderPath):
    url = 'http://144.126.222.53/transfer'               # Subject to change
    multiple_files=[]

    for file in os.listdir(folderPath):				# Clear folder on images from previous image capture sequence
        #('images', ("imageName.jpg",open(folderPath + file, 'rb'), 'image/jpg'))
        newFile = ('images', (file,open(folderPath + "/" + file, 'rb'), 'image/jpg'))
        multiple_files.append(newFile)

    print(multiple_files)
    r = requests.post(url, files=multiple_files)
    print(r.text)