from clarifai_grpc.channel.clarifai_channel import ClarifaiChannel
from clarifai_grpc.grpc.api import resources_pb2, service_pb2, service_pb2_grpc
from clarifai_grpc.grpc.api.status import status_code_pb2
import os
from os import listdir
import cv2 as cv
import numpy as np
#food-item-v1-recognition
#food-item-recognition

USER_ID = 'sikgaek'

PAT = '9f8278ad4e7a4549a7b1f43b9e538ec0'
APP_ID = 'Grocery-Tracker'
MODEL_ID = 'food-item-v1-recognition'

#folder_loc = r'C:\Users\jcam3\GitHub Repositories\ECE140B\GroupProject\GroceryTracker\Web-App\web\src\public\images'
#folder_loc2 = r'C:\Users\jcam3\GitHub Repositories\ECE140B\GroupProject\GroceryTracker\Web-App\web\src\processed_images'
folder_loc = r'C:\Users\ihyun\Desktop\GroceryTracker\Web-App\web\src\public\images'
folder_loc2 = r'C:\Users\ihyun\Desktop\GroceryTracker\Web-App\web\src\public\processed_images'

MODEL_VERSION_ID = ''


def img_pro(img, name):
    image = cv.imread(img, 1)
    gray = cv.cvtColor(image.copy(), cv.COLOR_BGR2GRAY)
    blur = cv.GaussianBlur(gray, (11, 11), 0)
    thresh = cv.threshold(blur, 0, 255, cv.THRESH_BINARY | cv.THRESH_OTSU)[1]
    invert = 255 - thresh
    kernel = np.array([[0., 1., 0.], [1.,1.,1.], [0., 1., 0.]], np.uint8)
    dilated = cv.dilate(invert, kernel)
    contours, hierarchy = cv.findContours(dilated, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    sort = sorted(contours, key = cv.contourArea, reverse = True)
    biggest = sort[0]
    first_contour = cv.drawContours(image.copy(), biggest, -1,(255,0,255),3)
    x, y, w, h = cv.boundingRect(biggest)
    cv.rectangle(first_contour,(x,y), (x+w,y+h), (255,0,0), 5)
    #cv.imshow('First contour with bounding box', first_contour)
    #cv.waitKey(0)
    #cv.destroyAllWindows()
    #print('Total number of contours detected: ' + str(len(contours)))
    result = image[y:y+h, x:x+w]
    # cv.imwrite("Result.png", result)
    file_path = os.path.join(folder_loc2, name)
    #print(file_path)
    cv.imwrite(file_path, result)
    return x

def tracking(img):
    channel = ClarifaiChannel.get_grpc_channel()
    stub = service_pb2_grpc.V2Stub(channel)

    metadata = (('authorization', 'Key ' + PAT),)

    userDataObject = resources_pb2.UserAppIDSet(user_id=USER_ID, app_id=APP_ID)

    with open(img, "rb") as f:
        file_bytes = f.read()

    post_model_outputs_response = stub.PostModelOutputs(
        service_pb2.PostModelOutputsRequest(
            user_app_id=userDataObject,  # The userDataObject is created in the overview and is required when using a PAT
            model_id=MODEL_ID,
            version_id=MODEL_VERSION_ID,  # This is optional. Defaults to the latest model version
            inputs=[
                resources_pb2.Input(
                    data=resources_pb2.Data(
                        image=resources_pb2.Image(
                            base64=file_bytes
                        )
                    )
                )
            ]
        ),
        metadata=metadata
    )
    if post_model_outputs_response.status.code != status_code_pb2.SUCCESS:
        print(post_model_outputs_response.status)
        raise Exception("Post model outputs failed, status: " + post_model_outputs_response.status.description)

    # Since we have one input, one output will exist here
    output = post_model_outputs_response.outputs[0]

    return output.data.concepts[0]
    #print("Outcome:")
    #print("%s %.3f" % (output.data.concepts[0].name, output.data.concepts[0].value))


    #for concept in output.data.concepts:
    #   print("%s %.2f" % (concept.name, concept.value))

def dup_img(x):
    prev = []
    for img in os.listdir(folder_loc2):
        img2 = os.path.join(folder_loc2, img)
        image = cv.imread(img2, 1)
        #print(np.size(prev))
        if np.size(prev) == 0:
            prev = image
            continue
        image = np.resize(image, (np.shape(prev)))
        avg = np.average(image - prev)
        #print(avg, img2)
        if avg < 30:
            os.remove(img2)
            '''if x - x2 > 0:
                mov = "OUT"
            else:
                mov = "IN"
            return mov'''
            prev = image
        prev = image
        x2 = x

if __name__ == "__main__":
    for img in os.listdir(folder_loc):
        if img == "received":
            continue
        img2 = os.path.join(folder_loc, img)
        x = img_pro(img2, img)
        dup_img(x)
        img3 = os.path.join(folder_loc2, img)
        #print(img3)
        try:
            data = tracking(img3)
        except:
            continue
        print("%s %.3f" % (data.name, data.value))