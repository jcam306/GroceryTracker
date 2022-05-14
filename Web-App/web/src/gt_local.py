from clarifai_grpc.channel.clarifai_channel import ClarifaiChannel
from clarifai_grpc.grpc.api import resources_pb2, service_pb2, service_pb2_grpc
from clarifai_grpc.grpc.api.status import status_code_pb2
import os
from os import listdir
import cv2 as cv
import numpy as np


USER_ID = 'sikgaek'
# Your PAT (Personal Access Token) can be found in the portal under Authentification
PAT = '9f8278ad4e7a4549a7b1f43b9e538ec0'
APP_ID = 'Grocery-Tracker'
MODEL_ID = 'aaa03c23b3724a16a56b629203edc62c'
# Change this to whatever image URL you want to process
folder_loc = r'C:\Users\ihyun\Desktop\GroceryTracker\Web-App\web\src\public\images'
# This is optional. You can specify a model version or the empty string for the default
MODEL_VERSION_ID = ''

############################################################################
# YOU DO NOT NEED TO CHANGE ANYTHING BELOW THIS LINE TO RUN THIS EXAMPLE
############################################################################

def img_pro(img):
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
    cv.imshow('First contour with bounding box', first_contour)
    cv.waitKey(0)
    cv.destroyAllWindows()
    print('Total number of contours detected: ' + str(len(contours)))


    result = image[y:y+h, x:x+w]
    cv.imwrite("Result.png", result)

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

    return output.data.concepts
    #print("Outcome:")
    #print("%s %.3f" % (output.data.concepts[0].name, output.data.concepts[0].value))


    #for concept in output.data.concepts:
    #   print("%s %.2f" % (concept.name, concept.value))
if __name__ == "__main__":
    for img in os.listdir(folder_loc):
        img2 = os.path.join(folder_loc, "milk.jpg")
        img_pro(img2)
        #data = tracking(img2)
        #print("%s %.3f" % (data.name, data.value))
