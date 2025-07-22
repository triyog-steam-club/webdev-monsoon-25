import requests
import google.generativeai as genai
from flask import current_app
import time
import os
import uuid

def get_ai_filtered_recipes(user_profile, ingredients):
    genai.configure(api_key=current_app.config['GEMINI_API_KEY'])
    edamam_params = {
        "q": " ".join(ingredients),
        "type": "public",
        "app_id": current_app.config['EDAMAM_APP_ID'],
        "app_key": current_app.config['EDAMAM_APP_KEY'],
        "random": "true" 
    }

    try:
        response = requests.get(current_app.config['EDAMAM_API_ENDPOINT'], params=edamam_params)
        response.raise_for_status() 
        recipes = response.json().get("hits", [])
    except requests.exceptions.RequestException as e:
        return {"error": f"Could not fetch recipes from Edamam: {e}"}, 500

    if not recipes:
        return {"message": "No recipes found for the given ingredients."}, 404

    model = genai.GenerativeModel('gemini-1.5-flash')
    
    suitable_recipes = []
    user_details = (
        f"User Profile: Age: {user_profile['age']}, "
        f"Gender: {user_profile['gender']}, "
        f"Weight: {user_profile['weight']}kg, "
        f"Height: {user_profile['height']}cm, "
        f"Health Concerns: {user_profile['disease']}"
    )

    for hit in recipes[-5]:
        recipe_data = hit['recipe']
        
        nutrient_summary = ", ".join([
            f"{int(n['total'])} {n['unit']} {n['label']}" 
            for n in recipe_data.get('digest', [])[:10] # First 10 major nutrients
        ])
        
        prompt = (
            "You are an expert nutritionist. Based on the following user health profile and recipe "
            "nutrition facts, is this recipe a healthy and suitable choice? "
            "Please answer ONLY with 'yes' or 'no'.\n\n"
            f"{user_details}\n\n"
            f"Recipe Name: {recipe_data['label']}\n"
            f"Recipe Nutrients: {nutrient_summary}\n\n"
            "Is this recipe suitable?"
        )

        print(prompt)

        try:
            ai_response = model.generate_content(prompt)
            decision = ai_response.text.strip().lower()

            if 'yes' in decision:
                suitable_recipes.append(recipe_data)
        except Exception as e:
            print(f"Error processing recipe with AI: {e}")
            continue

    if not suitable_recipes:
        return {"message": "Found recipes, but none were deemed suitable for the user's profile."}, 404

    return {"recipes": suitable_recipes}, 200

def generate_video_from_prompt(prompt):
    """
    Generates a video using the Veo model based on a text prompt,
    polls for completion, and saves the file.
    """
    # 1. Configure the client
    # This assumes the API key from config is already set up for the project
    genai.configure(api_key=current_app.config['GEMINI_API_KEY'])
    
    # 2. Create the video generation operation
    try:
        current_app.logger.info(f"Starting video generation for prompt: {prompt}")
        operation = genai.generate_videos(
            model="models/veo-1.0-generate-preview", # Use the specific model name
            prompt=prompt,
        )
    except Exception as e:
        current_app.logger.error(f"Error starting video generation: {e}")
        return {"error": f"Failed to start video generation process: {e}"}, 500

    # 3. Poll the operation status until the video is ready
    # WARNING: This is a blocking operation and is not suitable for a production server
    # without a background task runner (like Celery).
    current_app.logger.info(f"Polling for operation completion: {operation.operation.name}")
    while not operation.done:
        current_app.logger.info("Waiting for video generation to complete...")
        time.sleep(10)  # Poll every 10 seconds
        try:
            # The operation object automatically handles re-fetching its status
            operation.poll()
        except Exception as e:
            current_app.logger.error(f"Error polling operation status: {e}")
            return {"error": f"Failed while waiting for video: {e}"}, 500

    current_app.logger.info("Video generation completed.")
    
    # 4. Save the generated video file
    try:
        # Generate a unique filename to prevent overwrites
        unique_id = uuid.uuid4()
        filename = f"{unique_id}.mp4"
        save_path = os.path.join("generated_videos", filename)

        # Access the video data from the completed operation
        generated_video = operation.result.generated_videos[0]
        
        # Ensure the directory exists
        os.makedirs("generated_videos", exist_ok=True)

        # The SDK now has a convenient write_to_file method
        generated_video.video.write_to_file(save_path)
        
        current_app.logger.info(f"Generated video saved to {save_path}")
        return {"message": "Video generated successfully.", "filename": filename}, 200

    except Exception as e:
        current_app.logger.error(f"Error saving the generated video: {e}")
        return {"error": f"Failed to save video file after generation: {e}"}, 500