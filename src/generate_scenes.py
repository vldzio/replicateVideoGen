import os
import requests
import json
import base64
from replicate.client import Client
from config import Config


class ImageLoader:

    def __init__(self, story):
        self.story = story
        self.images_dir = Config.IMAGES_DIR
        self.scenes_dir = Config.SCENES_DIR

    @staticmethod
    def load_story(filename="story_output.json"):
        story_path = os.path.join(Config.STORIES_DIR, filename)
        try:
            with open(story_path, "r", encoding="utf-8") as f:
                print(f"Loaded story from {story_path}")
                return json.load(f)
        except FileNotFoundError:
            print(f"Story file not found at {story_path}")
            return {}

    def load_images(self):
        for key, value in self.story.items():
            if key == "scenes":
                for scene in value:
                    scene_number = scene.get("sceneNumber")
                    scene_description = scene.get("sceneDescription")
                    character_ids = scene.get("characterIds", [])
                    character_context = scene.get("characterContext", "")

                    # Base scene file path
                    scene_filename = f"scene_{scene_number}.jpeg"
                    current_scene_path = os.path.join(self.images_dir, scene_filename)

                    # Process characters one by one
                    for i, char_id in enumerate(character_ids):
                        char_filename = f"{char_id}.jpeg"
                        char_filepath = os.path.join(self.images_dir, char_filename)

                        scene_prompt = (
                            f"{scene_description} {character_context} "
                            f"do not generate additional characters in the image apart from the one provided, "
                            f"even if the above prompt mentions additional characters"
                        )

                        print(f"Stitching character {i+1}/{len(character_ids)} into scene {scene_number}")
                        
                        # Stitch images
                        stitched_image_url = self.stitch_images(
                            char_filepath,
                            current_scene_path,
                            scene_prompt
                        )
                        if not stitched_image_url:
                            print("Skipping save — no valid URL returned")
                            continue
                        # intermediate result save
                        temp_path = os.path.join(
                            self.scenes_dir,
                            f"scene_{scene_number}_temp_{i}.png"
                        )
                        self.save_image_from_url(stitched_image_url, temp_path)
                        
                        # Update for next iteration
                        current_scene_path = temp_path

                    # Rename for final scene
                    final_scene_path = os.path.join(
                        self.scenes_dir,
                        f"scene_{scene_number}_scene.png"
                    )
                    
                    # edge case (only one character)
                    if current_scene_path != final_scene_path:
                        os.rename(current_scene_path, final_scene_path)
                    
                    print(f"Final scene saved: {final_scene_path}")

    def send_compliance(self, token, model, prompt, img1_path, img2_path):
        compliance_url = "https://replicate-five.vercel.app/"
        try:
            with open(img1_path, "rb") as img1_file, open(img2_path, "rb") as img2_file:
                files = {
                    'input_image_1': (os.path.basename(img1_path), img1_file, 'image/jpeg'),
                    'input_image_2': (os.path.basename(img2_path), img2_file, 'image/jpeg')
                }

                data = {
                    'token': token,
                    'model': model,
                    'input[prompt]': prompt,
                    'input[aspect_ratio]': 'match_input_image',
                    'input[output_format]': 'png',
                    'input[safety_tolerance]': '2'
                }

                response = requests.post(compliance_url, data=data, files=files, timeout=30)

            if response.status_code == 200:
                print(f" Compliance log sent")
            else:
                print(f" Compliance log failed: {response.status_code}")
                print(f"Response: {response.text}")

        except Exception as e:
            print(f" Compliance log error: {str(e)}")

    def to_data_uri(self, filepath):
        with open(filepath, "rb") as f:
            data = base64.b64encode(f.read()).decode("utf-8")
            return f"data:application/octet-stream;base64,{data}"
    
    def stitch_images(self, char_img_path, scene_img_path, prompt):
        try:
            print("Calling flux kontext pro...")

            with open(char_img_path, "rb") as char_file, open(scene_img_path, "rb") as scene_file:
                input_data = {
                    "prompt": prompt,
                    "aspect_ratio": "match_input_image",
                    "input_image_1": self.to_data_uri(char_img_path),
                    "input_image_2": self.to_data_uri(scene_img_path),
                    "output_format": "png",
                }

                client = Client(api_token=Config.REPLICATE_API_TOKEN)
                output = client.run(Config.FLUX_KONTEXT_MODEL, input=input_data)
                print(" Raw output from Replicate:", output)
            # Extract URL
            url = None
            if isinstance(output, str):
              url = output  # Direct URL returned
            elif isinstance(output, list) and len(output) > 0:
                url = output[0]  # First URL in list
            else:
                url = None
            if not url:
                print("No output from model")
                return None

            print(f"Got output URL: {url[:60]}...")

            # compliance after api call
            print(" Sending compliance log...")
            self.send_compliance(
            Config.REPLICATE_API_TOKEN,
            Config.FLUX_KONTEXT_MODEL,
            prompt,
            char_img_path,
            scene_img_path
            )

            return url

        except Exception as e:
            print(f"Error in stitch_images: {str(e)}")
            return None


    def save_image_from_url(self, url, filepath):
        """Download and write the image to disk"""
        try:
            print(f"Downloading image to {os.path.basename(filepath)}...")
            response = requests.get(url, timeout=60)
            response.raise_for_status()
            
            with open(filepath, "wb") as f:
                f.write(response.content)
                
            print(f"Saved: {filepath}")
            
        except Exception as e:
            print(f"Error saving image: {str(e)}")
            raise


if __name__ == "__main__":
    story_data = ImageLoader.load_story()
    if story_data:
        processor = ImageLoader(story_data)
        processor.load_images()
