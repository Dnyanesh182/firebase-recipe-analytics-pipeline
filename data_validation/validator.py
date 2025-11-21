import csv
import json
import re
from collections import defaultdict

# --- CONFIGURATION ---
# Files are located in the 'transform_data' folder
FILES = {
    "recipes": ".\\transform_data\\recipes.csv",
    "ingredients": ".\\transform_data\\ingredients.csv",
    "steps": ".\\transform_data\\steps.csv",
    "interactions": ".\\transform_data\\interactions.csv"
}

VALID_DIFFICULTY = {"Easy", "Medium", "Hard", "Expert"}
NUMBER_REGEX = re.compile(r'^\d+(\.\d+)?$')

def load_csv_to_dict(filepath, key_field):
    """Loads CSV into a dictionary keyed by key_field."""
    data = {}
    try:
        with open(filepath, encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                data[row[key_field]] = row
    except FileNotFoundError:
        print(f"Warning: File not found: {filepath}")
    return data

def load_csv_to_grouped_dict(filepath, key_field):
    """Loads CSV into a dictionary of lists, grouped by key_field."""
    data = defaultdict(list)
    try:
        with open(filepath, encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                data[row[key_field]].append(row)
    except FileNotFoundError:
        print(f"Warning: File not found: {filepath}")
    return data

def parse_float(value):
    """Safely parses a float string."""
    if not value or value.strip() == "":
        return None
    try:
        return float(value)
    except ValueError:
        return None

def validate_time_integrity(rec, errors):
    """Validates prep, cook, and total time logic."""
    prep = parse_float(rec.get("prep_time_min"))
    cook = parse_float(rec.get("cook_time_min"))
    total = parse_float(rec.get("total_time_min"))

    if prep is not None and prep <= 0:
        errors.append(f"PrepTime must be > 0 (Got: {prep})")
    
    if cook is not None and cook < 0:
        errors.append(f"CookTime must be >= 0 (Got: {cook})")

    if total is None:
        errors.append("TotalTime missing")
    elif prep is not None and cook is not None:
        # Allow a small floating point margin
        if total < (prep + cook) - 0.1: 
            errors.append(f"TotalTime ({total}) < Prep ({prep}) + Cook ({cook})")

def validate_ingredients(rid, ingredients_list, errors):
    if not ingredients_list:
        errors.append("No ingredients linked to this recipe")
        return

    for ing in ingredients_list:
        qty = ing.get("quantity")
        if qty and NUMBER_REGEX.match(str(qty).strip()):
            if float(qty) <= 0:
                errors.append(f"Ingredient '{ing.get('name')}' has invalid quantity: {qty}")

def validate_interactions(interactions_list, errors):
    for inter in interactions_list:
        rstr = inter.get("rating")
        if rstr:
            val = parse_float(rstr)
            if val is None:
                errors.append(f"Rating '{rstr}' is not numeric")
            elif not (0 <= val <= 5):
                errors.append(f"Rating '{val}' out of range (0-5)")

def validate_recipes():
    print(f"Starting Data Validation...")

    # 1. Load Data
    print("Loading CSV files from 'transform_data' folder...")
    recipes = load_csv_to_dict(FILES["recipes"], 'recipe_id')
    ingredients = load_csv_to_grouped_dict(FILES["ingredients"], 'recipe_id')
    steps = load_csv_to_grouped_dict(FILES["steps"], 'recipe_id')
    interactions = load_csv_to_grouped_dict(FILES["interactions"], 'recipe_id')

    report = {
        "summary": {
            "total_recipes": len(recipes),
            "valid_recipes": 0,
            "invalid_recipes": 0,
            "missing_files": []
        },
        "invalid_records": [],
        "valid_records": []
    }

    # Check if main data exists
    if not recipes:
        print(f"❌ Error: No recipe data found. Exiting.")
        return

    # 2. Validation Loop
    for rid, rec in recipes.items():
        errors = []

        # A. Basic Field Checks
        if not rec.get("title"):
            errors.append("Missing Title")
        
        difficulty = rec.get("difficulty", "").strip()
        if difficulty and difficulty not in VALID_DIFFICULTY:
            errors.append(f"Invalid difficulty: '{difficulty}'")

        # B. Logic Checks
        validate_time_integrity(rec, errors)
        validate_ingredients(rid, ingredients.get(rid, []), errors)
        validate_interactions(interactions.get(rid, []), errors)

        # C. Structure Checks
        if not steps.get(rid):
            errors.append("No steps linked to this recipe")

        # D. Record Result
        if errors:
            report["invalid_records"].append({
                "recipe_id": rid,
                "title": rec.get("title", "Unknown"),
                "errors": errors
            })
        else:
            report["valid_records"].append(rid)

    # 3. Summarize
    report["summary"]["valid_recipes"] = len(report["valid_records"])
    report["summary"]["invalid_recipes"] = len(report["invalid_records"])

    # 4. Write Report
    output_path = "validation_report.json"
    with open(output_path, "w", encoding='utf-8') as f:
        json.dump(report, f, indent=2)

    print(f"Validation Complete.")
    print(f"✔ Valid: {report['summary']['valid_recipes']}")
    print(f"✖ Invalid: {report['summary']['invalid_recipes']}")
    print(f"Report saved to: {output_path}")

if __name__ == "__main__":
    validate_recipes()