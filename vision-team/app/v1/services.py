import requests
import google.generativeai as genai
from flask import current_app
import time
import os
import uuid
import re

def get_ai_filtered_recipes(user_profile, ingredients):
    """
    Fetches recipes from Edamam and uses a single AI call to filter them
    based on a user's health profile, reducing API usage.
    """
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
        recipes_hits = response.json().get("hits", [])
    except requests.exceptions.RequestException as e:
        return {"error": f"Could not fetch recipes from Edamam: {e}"}, 500

    if not recipes_hits:
        return {"message": "No recipes found for the given ingredients."}, 404

    model = genai.GenerativeModel('gemini-1.5-flash')

    # Prepare all recipe details for a single prompt
    recipes_to_evaluate = []
    recipe_details_for_prompt = ""
    for i, hit in enumerate(recipes_hits[:15]):  # Limit to the top 10 recipes to manage prompt size
        recipe_data = hit['recipe']
        recipes_to_evaluate.append(recipe_data) # Store the full recipe data
        
        nutrient_summary = ", ".join([
            f"{int(n['total'])} {n['unit']} {n['label']}"
            for n in recipe_data.get('digest', [])[:10] # First 10 major nutrients
        ])
        
        recipe_details_for_prompt += (
            f"Recipe Index: {i}\n"
            f"Recipe Name: {recipe_data['label']}\n"
            f"Nutrients: {nutrient_summary}\n\n"
        )

    user_details = (
        f"User Profile -> Age: {user_profile['age']}, "
        f"Gender: {user_profile['gender']}, "
        f"Weight: {user_profile['weight']}kg, "
        f"Height: {user_profile['height']}cm, "
        f"Health Concerns: {user_profile['disease']}"
    )

    # Create a single, comprehensive prompt
    prompt = (
        "You are an expert nutritionist. Based on the user's health profile, "
        "review the following list of recipes.\n"
        "Identify which recipes are a healthy and suitable choice.\n\n"
        f"User Details: {user_details}\n\n"
        "--- Recipes ---\n"
        f"{recipe_details_for_prompt}"
        "------\n\n"
        "Which of these recipes are suitable for the user? "
        "Please respond ONLY with a comma-separated list of the "
        "suitable 'Recipe Index' numbers (e.g., '0, 2, 5')."
    )
    
    print(prompt)

    try:
        ai_response = model.generate_content(prompt)
        # Use regex to safely find all numbers in the response string
        suitable_indices = re.findall(r'\d+', ai_response.text)
        suitable_indices = [int(i) for i in suitable_indices]

        suitable_recipes = [
            recipes_to_evaluate[i] for i in suitable_indices if i < len(recipes_to_evaluate)
        ]

    except Exception as e:
        print(f"Error processing recipes with AI: {e}")
        return {"error": f"Failed to get AI-based recipe recommendations: {e}"}, 500

    if not suitable_recipes:
        return {"message": "Found recipes, but none were deemed suitable for the user's profile."}, 404

    return {"recipes": suitable_recipes}, 200