import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

# Check to ensure app isn't initialized twice if running in a loop/notebook
if not firebase_admin._apps:
    cred = credentials.Certificate('config/serviceAccountKey.json')
    firebase_admin.initialize_app(cred)

db = firestore.client()

# --- 1. Define Dosa Data ---

dosa_ingredients = [
    {"name": "Idli Rice / Parboiled Rice", "Quantity": 3, "Unit": "cups", "Optional": False},
    {"name": "Urad Dal (Whole White Lentils)", "Quantity": 1, "Unit": "cup", "Optional": False},
    {"name": "Fenugreek Seeds (Methi)", "Quantity": 1, "Unit": "tsp", "Optional": False},
    {"name": "Salt", "Quantity": 2, "Unit": "tsp", "Optional": False},
    {"name": "Water", "Quantity": 1, "Unit": "liter", "Optional": False},
    {"name": "Oil or Ghee", "Quantity": 100, "Unit": "ml", "Optional": False},
    {"name": "Potato Masala (for Masala Dosa)", "Quantity": 1, "Unit": "bowl", "Optional": True}
]

dosa_steps = [
    {"StepNumber": 1, "Instruction": "Wash rice and dal thoroughly in separate bowls", "Duration": "10 min"},
    {"StepNumber": 2, "Instruction": "Soak rice and fenugreek seeds in water", "Duration": "4-6 hours"},
    {"StepNumber": 3, "Instruction": "Soak urad dal in water separately", "Duration": "4-6 hours"},
    {"StepNumber": 4, "Instruction": "Drain water. Grind urad dal to a fluffy, smooth batter", "Duration": "15 min"},
    {"StepNumber": 5, "Instruction": "Grind rice to a slightly coarse paste", "Duration": "15 min"},
    {"StepNumber": 6, "Instruction": "Mix both batters together in a large pot with salt", "Duration": "5 min"},
    {"StepNumber": 7, "Instruction": "Cover and let ferment in a warm place", "Duration": "8 hours"},
    {"StepNumber": 8, "Instruction": "Heat a cast iron tawa or non-stick pan on medium heat", "Duration": "2 min"},
    {"StepNumber": 9, "Instruction": "Pour a ladle of batter and spread in a circular motion", "Duration": "30 sec"},
    {"StepNumber": 10, "Instruction": "Drizzle 1 tsp oil/ghee around the edges", "Duration": "10 sec"},
    {"StepNumber": 11, "Instruction": "Cook until the bottom turns golden brown and crisp", "Duration": "2 min"},
    {"StepNumber": 12, "Instruction": "Fold the dosa (add potato masala now if desired) and remove", "Duration": "30 sec"},
    {"StepNumber": 13, "Instruction": "Serve hot with chutney and sambar", "Duration": "1 min"},
]

# --- 2. Add Recipe to Firestore ---

recipe_ref = db.collection("Recipe").document()

recipe_ref.set({
    "Title": "Crispy Dosa",
    "Description": "South Indian fermented crepe made from rice and lentil batter.",
    "Ingredients": dosa_ingredients,
    "Steps": dosa_steps,
    "TimeRequired": {
        "PrepTime": 30,       # Active prep time
        "RestTime": 480,      # Fermentation (8 hours)
        "CookTime": 30,       # Cooking time for a batch
        "TotalTime": 540
    },
    "Difficulty": "Medium",
    "CreatedAt": datetime.now(),
    "AuthorID": "user_12345",
    "AuthorName": "Dnyaneshwarpotdar"
})

print("Dosa Recipe Added. ID:", recipe_ref.id)

# --- 3. Add Interaction (Rating/Comment) ---

interaction_ref = recipe_ref.collection("Interaction").document()

interaction_ref.set({
    "username": "dnyaneshwarpotdar",
    "userID": "user_12345",
    "type": "rating",
    "rating": "5",
    "cooknote": "Batter fermented perfectly! Very crispy.",
    "recipename": "Crispy Dosa",
    "createdAt": datetime.now()
})

print("Interaction added for:", recipe_ref.id)

# --- 4. Create User & Log Activity ---

user_ref = db.collection("Users").document()

user_data = {
    "UserID": user_ref.id,
    "UserName": "SouthIndianFoodie",
    "Email": "dosaLover@gmail.com",
    "Mobile Number": "9876543210",
    "Joined At": datetime.now(),
    "Skill Level": "Intermediate"
}

user_ref.set(user_data)
print("User created with ID:", user_ref.id)

activity_ref = user_ref.collection("Activities").document()

activity_data = {
    "Activity ID": activity_ref.id,
    "Recipe Name": "Crispy Dosa",
    "Type": "Like",
    "rating": "0",
    "cooknote": "Batter fermented perfectly! Very crispy.",
    "CreatedAt": datetime.now()
}

activity_ref.set(activity_data)
print("Activity added for user:", user_ref.id)