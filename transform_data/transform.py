import firebase_admin
from firebase_admin import credentials, firestore
import csv
import os
import json
from datetime import datetime

# --- CONFIGURATION ---
KEY_PATH = 'config/serviceAccountKey.json'

# --- 1. INITIALIZE FIREBASE (EXTRACT) ---
if not firebase_admin._apps:
    if os.path.exists(KEY_PATH):
        with open(KEY_PATH, 'r') as readfile:
            service_account_info = json.load(readfile)
        cred = credentials.Certificate(service_account_info)
        firebase_admin.initialize_app(cred)
    else:
        print(f"Error: Key file not found at {KEY_PATH}")
        exit()

db = firestore.client()

def clean_timestamp(ts):
    """Helper to convert Firestore Timestamp to ISO string."""
    if ts:
        return ts.isoformat()
    return ""

# --- 2. TRANSFORM LOGIC ---
def run_etl_process():
    print("Starting ETL Process...")
    
    # Data containers for normalized tables
    recipes_table = []
    ingredients_table = []
    steps_table = []
    interactions_table = []

    # Fetch all recipes
    docs = db.collection("Recipe").stream()
    
    count = 0
    for doc in docs:
        count += 1
        data = doc.to_dict()
        recipe_id = doc.id
        
        print(f"Processing Recipe: {data.get('Title', 'Unknown')}")

        # --- TRANSFORM RECIPE (Parent Table) ---
        time_info = data.get("TimeRequired", {})
        
        recipe_row = {
            "recipe_id": recipe_id,
            "title": data.get("Title"),
            "description": data.get("Description"),
            "prep_time_min": time_info.get("PrepTime"),
            "cook_time_min": time_info.get("CookTime"),
            "total_time_min": time_info.get("TotalTime"),
            "difficulty": data.get("Difficulty"),
            "category": data.get("Category", "Uncategorized"),
            "dietary_type": data.get("DietaryType", "Unknown"),
            "author_id": data.get("AuthorID"),
            "author_name": data.get("AuthorName"),
            "created_at": clean_timestamp(data.get("CreatedAt"))
        }
        recipes_table.append(recipe_row)

        # --- TRANSFORM INGREDIENTS (Child Table) ---
        # One-to-Many relationship: One Recipe -> Many Ingredients
        raw_ingredients = data.get("Ingredients", [])
        for ing in raw_ingredients:
            ing_row = {
                "recipe_id": recipe_id,
                "name": ing.get("name"),
                "quantity": ing.get("Quantity"),
                "unit": ing.get("Unit"),
                "is_optional": ing.get("Optional", False)
            }
            ingredients_table.append(ing_row)

        # --- TRANSFORM STEPS (Child Table) ---
        # One-to-Many relationship: One Recipe -> Many Steps
        raw_steps = data.get("Steps", [])
        for step in raw_steps:
            step_row = {
                "recipe_id": recipe_id,
                "step_number": step.get("StepNumber"),
                "instruction": step.get("Instruction"),
                "duration": step.get("Duration")
            }
            steps_table.append(step_row)

        # --- TRANSFORM INTERACTIONS (Sub-collection Extraction) ---
        # Fetch sub-collection 'Interaction' for this specific recipe
        interactions = doc.reference.collection("Interaction").stream()
        
        for interaction in interactions:
            idata = interaction.to_dict()
            interaction_row = {
                "interaction_id": interaction.id,
                "recipe_id": recipe_id, # Foreign Key
                "user_id": idata.get("userID"),
                "username": idata.get("username"),
                "type": idata.get("type"),
                "rating": idata.get("rating"),
                "cooknote": idata.get("cooknote"),
                "created_at": clean_timestamp(idata.get("createdAt"))
            }
            interactions_table.append(interaction_row)

    # --- 3. LOAD (Export to CSV) ---
    print(f"\nExtraction complete. Processed {count} recipes.")
    print("Writing to CSV...")

    # Helper to write CSV
    def write_csv(filename, fieldnames, data_list):
        # Modified to save in the same folder (current directory)
        filepath = filename 
        with open(filepath, mode='w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data_list)
        print(f"✔ Generated {filename} ({len(data_list)} rows)")

    # Write Recipes
    write_csv('recipes.csv', 
              ["recipe_id", "title", "description", "prep_time_min", "cook_time_min", 
               "total_time_min", "difficulty", "category", "dietary_type", 
               "author_id", "author_name", "created_at"], 
              recipes_table)

    # Write Ingredients
    write_csv('ingredients.csv', 
              ["recipe_id", "name", "quantity", "unit", "is_optional"], 
              ingredients_table)

    # Write Steps
    write_csv('steps.csv', 
              ["recipe_id", "step_number", "instruction", "duration"], 
              steps_table)

    # Write Interactions
    write_csv('interactions.csv', 
              ["interaction_id", "recipe_id", "user_id", "username", 
               "type", "rating", "cooknote", "created_at"], 
              interactions_table)

    print(f"\nETL Pipeline Finished successfully. Data saved to current folder.")

if __name__ == "__main__":
    run_etl_process()