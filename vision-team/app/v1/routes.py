from flask import request, jsonify
from . import bp
from .services import get_ai_filtered_recipes
from .schemas import validate_recipe_request

@bp.route('/generate-recipes', methods=['POST'])
def generate_recipes_route():
    """
    Generate Personalized Recipe Recommendations
    This endpoint generates recipe recommendations based on a user's health profile and a list of ingredients.
    ---
    tags:
      - Recipe Generation
    requestBody:
      description: User profile and ingredient data
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              age:
                type: integer
                description: Age of the user in years.
                example: 30
              gender:
                type: string
                description: Gender of the user.
                example: "female"
              weight:
                type: number
                description: Weight of the user in kilograms.
                example: 65
              height:
                type: number
                description: Height of the user in centimeters.
                example: 170
              disease:
                type: string
                description: Any known health concerns or diseases.
                example: "high cholesterol"
              ingredients:
                type: array
                items:
                  type: string
                description: A list of ingredients to base the recipe on.
                example: ["chicken", "broccoli", "garlic"]
            required:
              - age
              - gender
              - weight
              - height
              - disease
              - ingredients
    responses:
      200:
        description: A list of suitable recipes was found.
        content:
          application/json:
            schema:
              type: object
              properties:
                recipes:
                  type: array
                  items:
                    type: object
                    description: A recipe object from the Edamam API.
      400:
        description: Bad Request. The request body is missing, invalid, or fails validation.
        content:
          application/json:
            schema:
              type: object
              properties:
                error:
                  type: string
                  example: "Validation failed"
                messages:
                  type: array
                  items:
                    type: string
                  example: ["Missing required field: 'age'"]
      404:
        description: Not Found. No recipes were found, or none were deemed suitable.
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
                  example: "No recipes found for the given ingredients."
      500:
        description: Internal Server Error. An error occurred while communicating with an external API.
        content:
          application/json:
            schema:
              type: object
              properties:
                error:
                  type: string
                  example: "Could not fetch recipes from Edamam: [Error Details]"
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON provided."}), 400

    errors = validate_recipe_request(data)
    if errors:
        return jsonify({"error": "Validation failed", "messages": errors}), 400

    user_profile = {
        "age": data.get("age"),
        "gender": data.get("gender"),
        "weight": data.get("weight"),
        "height": data.get("height"),
        "disease": data.get("disease")
    }
    ingredients = data.get("ingredients")

    result, status_code = get_ai_filtered_recipes(user_profile, ingredients)
    return jsonify(result), status_code