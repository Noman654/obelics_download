#pip3 install "google-cloud-aiplatform>=1.38"

import os
import pandas as pd
from time import sleep
import vertexai
from vertexai.generative_models import GenerativeModel, Part, Image

project_id = "aigeminikrutrim-425306"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="/Users/abhinav.ravi/Downloads/aigeminikrutrim.json"
vertexai.init(project=project_id, location="asia-south1")
model = GenerativeModel(model_name="gemini-1.0-pro-vision")

img_root_dir = '/Users/abhinav.ravi/Downloads/diwali/'
file_names = os.listdir(img_root_dir)

save_file_name = './vertex_ai_test.csv'
if os.path.exists(save_file_name):
    os.remove(save_file_name)

query_prompt= "Pls suggest a 1-2 lines description for this image which would be fed into a vision language model for image generation task."


df = pd.DataFrame(columns=['image_name', 'description'])

for i, curr_file in enumerate(file_names[2058:2070]):
    try: 
        image_file = Image.load_from_file(img_root_dir + curr_file)
        print(curr_file)
        # Query the model
        response = model.generate_content([image_file, query_prompt])
        print(i, response.text)
        df = df.append({'image_name': curr_file, 'description':response.text}, ignore_index=True)
        if(i % 4 ==0):
            df.to_csv(save_file_name, index=False)
    except Exception as ex:
        print(ex)