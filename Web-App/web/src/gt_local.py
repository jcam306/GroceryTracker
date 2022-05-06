from clarifai_grpc.channel.clarifai_channel import ClarifaiChannel
from clarifai_grpc.grpc.api import resources_pb2, service_pb2, service_pb2_grpc
from clarifai_grpc.grpc.api.status import status_code_pb2
import os
from os import listdir


USER_ID = 'sikgaek'
# Your PAT (Personal Access Token) can be found in the portal under Authentification
PAT = '9f8278ad4e7a4549a7b1f43b9e538ec0'
APP_ID = 'Grocery-Tracker'
MODEL_ID = 'aaa03c23b3724a16a56b629203edc62c'
# Change this to whatever image URL you want to process
folder_loc = r'C:\Users\ihyun\Desktop\GroceryTracker\local\images'
# This is optional. You can specify a model version or the empty string for the default
MODEL_VERSION_ID = ''

############################################################################
# YOU DO NOT NEED TO CHANGE ANYTHING BELOW THIS LINE TO RUN THIS EXAMPLE
############################################################################
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
if __name__ == "__main__":
    for img in os.listdir(folder_loc):
        img2 = os.path.join(folder_loc, img)
        data = tracking(img2)
        print("%s %.3f" % (data.name, data.value))
