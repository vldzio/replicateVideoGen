import os
import json
import requests
from replicate.client import Client
from config import Config


class StoryProcessor:
    def __init__(self, story_file="story_output.json"):
        STORIES_DIR = Config.STORIES_DIR
        self.story_file_path = os.path.join(STORIES_DIR, story_file)
        self.story = None

    def load_story(self):
        try:
            with open(self.story_file_path, 'r', encoding='utf-8') as f:
                self.story = json.load(f)
            print(f"Loaded story from {self.story_file_path}")
        except FileNotFoundError:
            print(f"Error: Story file not found at {self.story_file_path}")
            self.story = {}

    def process_characters(self):
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

    def generateImage(self, prompt_data, identifier):
        input_data = {
            "prompt": prompt_data,
            "aspect_ratio": "16:9",
            "number_of_images": 1,
            "prompt_optimizer": True
        }
        try:
            print(f"Generating image for {identifier}...")
            Config.validate()
            client = Client(api_token=Config.REPLICATE_API_TOKEN)
            output = client.run(Config.MINIMAX_MODEL, input=input_data)
            
            IMAGES_DIR = Config.IMAGES_DIR
            os.makedirs(IMAGES_DIR, exist_ok=True)

            for index, item in enumerate(output):
                if isinstance(identifier, str):
                    filename = f"{identifier}.jpeg"
                else:
                    filename = f"scene_{identifier}.jpeg"

                file_path = os.path.join(IMAGES_DIR, filename)
                with open(file_path, "wb") as file:
                    file.write(item.read() if hasattr(item, 'read') else requests.get(item).content)
            print(f"✓ Saved image to {file_path}")
        except Exception as e:
            print(f"Image generation error: {str(e)}")


if __name__ == "__main__":
    processor = StoryProcessor()
    processor.load_story()
    processor.process_characters()
    processor.process_scenes()
