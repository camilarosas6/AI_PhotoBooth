import os
import base64
from openai import OpenAI

class OpenAIClient:
    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )

    def get_style_prompt(self, style):
        prompts = {
            "PIXAR":  (
                "Transform the photo into a Pixar-style animated character",
                "but give them the exaggerated proportions and vibrant colors typical of Pixar characters",
                "if the person is wearing glasses, has a beard or a mustache or any birthmarks, make sure to include them in the transformation",
                "if there is no one in the photo, create a Pixar-style character based on the background and context of the image"
            ),

            "ANIME": (
                "Transform the photo into an anime-style character",
                "keep the person's identity and facial features recognizable,"
                "but give them the exaggerated proportions and vibrant colors typical of anime characters",
                "if there is no one in the photo, create an anime-style character based on the background and context of the image"
            ),

            "SCRIBBLE" : (
                "Transform the photo into a playful hand-drawn scribble illustration",
                "keep the person recognizable, include facial features and do not erase anything from the photo, even in the background",
                "preserve the main composition and if there is no one in the photo, make everything look like this hand-drawn illustration"
            ),

            "CYBERPUNK" : (
                "Transform the photo into a futuristic cyberpunk portrait with neon lightning",
                "high-tech details and cinematic atmosphere",
                "keep the person recognizable, make sure to include all of the facial features and everything on the background"
            )

        }

        return ", ".join(prompts.get(style, prompts["ANIME"]))

    def generate_img(self, image, style):
        prompt = self.get_style_prompt(style)

        image_path = "temp_original.png"
        image_save = (image_path)

        with open(image_path, "rb") as image_file:
            result = self.client.images.edit(
                model="gpt-image-2",
                image = image_file,
                prompt = prompt
            )

        image_base64 = result.data[0].b64_json
        return base64.b64decode(image_base64)
