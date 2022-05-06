import requests
import os

def sendFolder(folderPath):
    url = 'http://localhost/transfer'               # Subject to change
    multiple_files=[]
    
    for file in os.listdir(folderPath):				# Clear folder on images from previous image capture sequence
        #('images', ("imageName.jpg",open(folderPath + file, 'rb'), 'image/jpg'))
        newFile = ('images', ("imageName.jpg",open(folderPath + file, 'rb'), 'image/jpg'))
        multiple_files.append(newFile)

    print(multiple_files)
    r = requests.post(url, files=multiple_files)
    print(r.text)

    # multiple_files = [
    # ('images', ('apple.jpg', open('./public/images/apple.jpg', 'rb'), 'image/jpg')),
    # ('images', ('bananas.jpg', open('./public/images/bananas.jpg', 'rb'), 'image/jpg'))]