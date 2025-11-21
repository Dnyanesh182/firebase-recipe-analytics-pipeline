import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import random

# Check if app is already initialized to avoid errors on re-run
if not firebase_admin._apps:
    cred = credentials.Certificate('config/serviceAccountKey.json')
    firebase_admin.initialize_app(cred)

db = firestore.client()

# --- NEW DATASET: Maharashtrian Cuisine ---

recipe_titles = [
    "Misal Pav", "Vada Pav", "Puran Poli", "Thalipeeth", 
    "Bharli Vangi (Stuffed Eggplant)", "Sabudana Khichdi", "Modak", "Pithla Bhakri",
    "Kothimbir Vadi", "Solkadhi", "Pav Bhaji", "Shrikhand",
    "Batata Vada", "Matki Usal", "Alu Vadi", "Bombil Fry",
    "Kolhapuri Mutton", "Masale Bhaat", "Dadpe Pohe", "Kanda Poha",
    "Sheera", "Rassa (Tambada/Pandhra)", "Ukadiche Modak"
]

# Authentic Maharashtrian pantry items
ingredient_pool = [
    "Besan (Gram Flour)", "Jaggery (Gul)", "Grated Coconut", "Goda Masala", 
    "Tamarind", "Kokum", "Peanuts", "Poha (Flattened Rice)", "Sabudana",
    "Rice Flour", "Mustard Seeds", "Curry Leaves", "Green Chilies", 
    "Brinjal (Eggplant)", "Potatoes", "Matki (Moth Beans)", "Tur Dal",
    "Chana Dal", "Coriander Leaves", "Garlic", "Ginger", "Oil", "Ghee",
    "Turmeric", "Red Chili Powder", "Asafoetida (Hing)", "Bombay Duck (Fish)"
]

units = ["grams", "tsp", "tbsp", "cups", "ml", "vati (bowl)", "pieces"]

difficulty_levels = ["Easy", "Medium", "Hard"]

interaction_types = ["view", "rating", "like", "cooknote", "share"]

# Localized usernames
sample_users = [
    {"userID": "user_MH01", "username": "Puneri_Maushi"},
    {"userID": "user_MH02", "username": "Mumbai_Cha_Raja"},
    {"userID": "user_MH03", "username": "Kolhapuri_Spiceman"},
    {"userID": "user_MH04", "username": "Konkan_Chef"},
    {"userID": "user_MH05", "username": "Nagpur_Foodie"}
]

def generate_ingredients():
    ingredients = []
    # Pick 6 to 12 random ingredients
    num_ingredients = random.randint(6, 12)
    selected_items = random.sample(ingredient_pool, num_ingredients)
    
    for item in selected_items:
        ingredients.append({
            "name": item,
            "Quantity": random.randint(1, 250),
            "Unit": random.choice(units),
            "Optional": random.choice([True, False])
        })
    return ingredients

def generate_steps():
    steps = []
    # Verbs common in Maharashtrian cooking
    verbs = ["Tempering (Phodni)", "Sauté", "Steam", "Knead", "Roll", "Deep Fry", "Garnish", "Pressure Cook"]
    
    for i in range(1, random.randint(5, 10)):
        verb = random.choice(verbs)
        steps.append({
            "StepNumber": i,
            "Instruction": f"{verb} the mixture properly for authentic taste.",
            "Duration": f"{random.randint(2, 15)} min"
        })
    return steps

def generate_interaction(recipe_ref, recipe_title):
    user = random.choice(sample_users)
    
    interaction_ref = recipe_ref.collection("Interaction").document()
    interaction_ref.set({
        "username": user["username"],
        "userID": user["userID"],
        "type": random.choice(interaction_types),
        "rating": str(random.randint(3, 5)), 
        "cooknote": "Lai bhari! (Awesome)" if random.random() > 0.6 else "Mast zala hota.",
        "recipename": recipe_title,
        "createdAt": datetime.now()
    })

# --- EXECUTION LOOP ---

# Generate 20 Maharashtrian recipes
for i in range(20): 
    title = random.choice(recipe_titles)
    author = random.choice(sample_users)

    recipe_ref = db.collection("Recipe").document()

    prep = random.randint(15, 40)
    cook = random.randint(20, 60)
    
    recipe_ref.set({
        "Title": title,
        "Description": f"Traditional Maharashtrian style {title}.",
        "Ingredients": generate_ingredients(),
        "Steps": generate_steps(),
        "TimeRequired": {
            "PrepTime": prep,
            "CookTime": cook,
            "TotalTime": prep + cook
        },
        "Difficulty": random.choice(difficulty_levels),
        "CreatedAt": datetime.now(),
        "AuthorID": author["userID"],
        "AuthorName": author["username"]
    })

    # Create random interactions
    for _ in range(random.randint(1, 4)):
        generate_interaction(recipe_ref, title)

    print(f"✔ Recipe {i+1} created: {title} (ID: {recipe_ref.id})")

print("\n--- Maharashtrian Data Generation Complete ---")