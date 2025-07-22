def validate_recipe_request(data):
    errors = []
    required_fields = ["age", "gender", "weight", "height", "disease", "ingredients"]

    for field in required_fields:
        if field not in data:
            errors.append(f"Missing required field: '{field}'")
    
    if "ingredients" in data and not isinstance(data["ingredients"], list):
        errors.append("'ingredients' must be a list of strings.")

    if "ingredients" in data and isinstance(data["ingredients"], list) and not data["ingredients"]:
        errors.append("'ingredients' list cannot be empty.")
        
    
    return errors