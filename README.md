# 🍳 Recipe Analytics ETL Pipeline

A complete data engineering pipeline built on Firebase Firestore for recipe data extraction, transformation, validation, and analytics. Features authentic Maharashtrian cuisine dataset with 20+ recipes.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Firebase](https://img.shields.io/badge/Firebase-Firestore-orange.svg)](https://firebase.google.com/)
[![Pandas](https://img.shields.io/badge/Pandas-Data%20Analysis-150458.svg)](https://pandas.pydata.org/)

---

## 📋 Table of Contents

1. [Data Model](#1-data-model)
2. [Project Structure](#2-project-structure)
3. [Instructions for Running the Pipeline](#3-instructions-for-running-the-pipeline)
4. [ETL Process Overview](#4-etl-process-overview)
5. [Data Validation](#5-data-validation)
6. [Insights Summary](#6-insights-summary)
7. [Known Constraints & Limitations](#7-known-constraints--limitations)
8. [Deliverables](#8-deliverables)

---

## 1. Data Model

### 1.1 Entity Relationship Diagram

<img width="1147" height="788" alt="ERD Diagram" src="https://github.com/user-attachments/assets/3f415152-5003-4c92-b04b-2d0b1ab73c3b" />


### 1.2 Why Subcollections?

| Design Choice | Reasoning |
|---------------|-----------|
| **Interactions under Recipes** | Groups recipe activity together; enables fast queries for single recipe analytics |
| **Activities under Users** | Tracks user behavior across recipes; enables user-centric analytics |
| **Denormalized author names** | Avoids extra reads; Firestore doesn't support JOINs |

---

## 2. Project Structure

```
RECIPE_ANALYTICS/
│
├── 📁 analytics/                    # Analytics outputs
│   ├── 📁 charts/                   # Generated visualizations
│   │   ├── 🖼 cook_time_histogram.png
│   │   ├── 🖼 difficulty_donut_chart.png
│   │   ├── 🖼 prep_vs_rating_scatter_plot.png
│   │   └── 🖼 top_ingredients_bar_chart.png
│   ├── 📄 analytics_summary.json    # All insights in JSON
│   ├── 🐍 analytics.py              # Analytics generation script
│   ├── 📊 most_common_ingredients.csv
│   └── 📊 top_rated_recipes.csv
│
├── 📁 config/                       # Configuration files
│   └── 🔑 serviceAccountKey.json    # Firebase credentials
│
├── 📁 data_validation/              # Validation outputs
│   ├── 📄 validation_report.json    # Quality check results
│   └── 🐍 validator.py              # Validation script
│
├── 📁 Firebase_Setup/               # Data seeding scripts
│   ├── 🐍 genrate_sytetic.py        # Generate 20 synthetic recipes
│   └── 🐍 seed_data.py              # Seed initial recipe (Dosa)
│
├── 📁 transform_data/               # ETL outputs (CSV)
│   ├── 📊 ingredients.csv           # Normalized ingredients
│   ├── 📊 interactions.csv          # User interactions
│   ├── 📊 recipes.csv               # Main recipe data
│   ├── 📊 steps.csv                 # Recipe steps
│   └── 🐍 transform.py              # ETL transformation script
│
├── 📁 .venv/                        # Python virtual environment
└── 📄 README.md                     # This file
```

---

## 3. Instructions for Running the Pipeline

### 3.1 Prerequisites

- Python 3.8 or higher
- Firebase project with Firestore enabled
- Service account credentials (JSON)

### 3.2 Installation

```bash
# Step 1: Clone the repository
git clone https://github.com/dnyanesh182/recipe-analytics.git
cd RECIPE_ANALYTICS

# Step 2: Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate        # Linux/Mac
.venv\Scripts\activate           # Windows

# Step 3: Install dependencies
pip install firebase-admin pandas matplotlib numpy google-cloud-firestore
```

### 3.3 Firebase Configuration

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select your project → Project Settings → Service Accounts
3. Click "Generate new private key"
4. Save the JSON file as `config/serviceAccountKey.json`

### 3.4 Run the Pipeline

Execute each step in order:

```bash
# ┌─────────────────────────────────────────────────────────────┐
# │  STEP 1: Seed Initial Data (Crispy Dosa Recipe)            │
# └─────────────────────────────────────────────────────────────┘
cd Firebase_Setup
python seed_data.py
# ✓ Creates: 1 recipe + 1 user + sample interactions

# ┌─────────────────────────────────────────────────────────────┐
# │  STEP 2: Generate Synthetic Data (20 Maharashtrian Recipes)│
# └─────────────────────────────────────────────────────────────┘
python genrate_sytetic.py
# ✓ Creates: 20 recipes with random interactions

# ┌─────────────────────────────────────────────────────────────┐
# │  STEP 3: Transform Firestore → CSV                         │
# └─────────────────────────────────────────────────────────────┘
cd ../transform_data
python transform.py
# ✓ Outputs: recipes.csv, ingredients.csv, steps.csv, interactions.csv

# ┌─────────────────────────────────────────────────────────────┐
# │  STEP 4: Validate Data Quality                             │
# └─────────────────────────────────────────────────────────────┘
cd ../data_validation
python validator.py
# ✓ Outputs: validation_report.json

# ┌─────────────────────────────────────────────────────────────┐
# │  STEP 5: Generate Analytics & Charts                       │
# └─────────────────────────────────────────────────────────────┘
cd ../analytics
python analytics.py
# ✓ Outputs: analytics_summary.json, charts/, CSV reports
```

---

## 4. ETL Process Overview

### 4.1 Pipeline Architecture

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   EXTRACT    │────►│  TRANSFORM   │────►│   VALIDATE   │────►│   ANALYZE    │
│              │     │              │     │              │     │              │
│  Firestore   │     │  Normalize   │     │   Quality    │     │   Insights   │
│  Database    │     │  & Flatten   │     │   Checks     │     │   & Charts   │
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
       │                    │                    │                    │
       ▼                    ▼                    ▼                    ▼
   Recipe &            4 CSV Files          validation_         analytics_
   Interaction         (Normalized)         report.json         summary.json
   Collections                                                  + charts/
```

### 4.2 Extract Phase (`transform.py`)

**Source:** Firebase Firestore  
**Method:** Firebase Admin SDK with streaming

```python
# Connect to Firestore
db = firestore.client()

# Stream all recipes
docs = db.collection("Recipe").stream()

# For each recipe, fetch subcollection
for doc in docs:
    interactions = doc.reference.collection("Interaction").stream()
```

**Operations:**

- Authenticates using service account credentials
- Streams documents to handle large collections efficiently
- Extracts nested Interaction subcollections per recipe
- Converts Firestore timestamps to ISO 8601 strings

### 4.3 Transform Phase (`transform.py`)

| Transformation | Before | After |
|----------------|--------|-------|
| **Flatten Ingredients** | Nested array in recipe | Separate `ingredients.csv` with `recipe_id` FK |
| **Flatten Steps** | Nested array in recipe | Separate `steps.csv` with `recipe_id` FK |
| **Extract Subcollections** | Firestore subcollection | `interactions.csv` with `recipe_id` FK |
| **Normalize Time** | `{PrepTime, CookTime, TotalTime}` | `prep_time_min`, `cook_time_min`, `total_time_min` |
| **Handle Missing** | Missing fields | Default: "Uncategorized", "Unknown" |
| **Timestamp Conversion** | Firestore Timestamp | ISO string format |

### 4.4 Output Schema (Normalized Tables)

```
recipes.csv                          ingredients.csv
┌────────────────────────────┐       ┌─────────────────────────┐
│ recipe_id (PK)             │       │ recipe_id (FK)          │
│ title                      │       │ name                    │
│ description                │◄──────│ quantity                │
│ prep_time_min              │       │ unit                    │
│ cook_time_min              │       │ is_optional             │
│ total_time_min             │       └─────────────────────────┘
│ difficulty                 │
│ category                   │       steps.csv
│ dietary_type               │       ┌─────────────────────────┐
│ author_id                  │       │ recipe_id (FK)          │
│ author_name                │◄──────│ step_number             │
│ created_at                 │       │ instruction             │
└────────────────────────────┘       │ duration                │
              ▲                      └─────────────────────────┘
              │
              │                      interactions.csv
              │                      ┌─────────────────────────┐
              └──────────────────────│ interaction_id (PK)     │
                                     │ recipe_id (FK)          │
                                     │ user_id                 │
                                     │ username                │
                                     │ type                    │
                                     │ rating                  │
                                     │ cooknote                │
                                     │ created_at              │
                                     └─────────────────────────┘
```

---

## 5. Data Validation

### 5.1 Validation Rules (`validator.py`)

| Rule | Field | Criteria |
|------|-------|----------|
| **Required Fields** | `title` | Must not be empty |
| **Valid Difficulty** | `difficulty` | Must be: Easy, Medium, Hard, Expert |
| **Prep Time** | `prep_time_min` | Must be > 0 |
| **Cook Time** | `cook_time_min` | Must be ≥ 0 |
| **Time Logic** | `total_time_min` | Must be ≥ prep_time + cook_time |
| **Ingredient Quantity** | `quantity` | Must be > 0 if numeric |
| **Rating Range** | `rating` | Must be between 0 and 5 |
| **Has Steps** | `steps` | At least one step required |
| **Has Ingredients** | `ingredients` | At least one ingredient required |

### 5.2 Validation Report Output

```json
{
  "summary": {
    "total_recipes": 21,
    "valid_recipes": 18,
    "invalid_recipes": 3
  },
  "invalid_records": [
    {
      "recipe_id": "abc123",
      "title": "Test Recipe",
      "errors": [
        "Invalid difficulty: 'Super Hard'",
        "TotalTime (30) < Prep (20) + Cook (25)"
      ]
    }
  ],
  "valid_records": ["id1", "id2", "id3", "..."]
}
```

---

## 6. Insights Summary

### 6.1 Analytics Generated (11 Insights)

| # | Insight | Description | Output Location |
|---|---------|-------------|-----------------|
| 1 | **Most Common Ingredients** | Top 20 ingredients by frequency | `most_common_ingredients.csv` |
| 2 | **Average Prep Time** | Mean preparation time (minutes) | `analytics_summary.json` |
| 3 | **Average Cook Time** | Mean cooking time (minutes) | `analytics_summary.json` |
| 4 | **Difficulty Distribution** | Count per difficulty level | `difficulty_donut_chart.png` |
| 5 | **Most Interacted Recipes** | Top 20 by interaction count | `analytics_summary.json` |
| 6 | **Prep vs Rating Correlation** | Statistical correlation | `prep_vs_rating_scatter_plot.png` |
| 7 | **High-Rating Ingredients** | Ingredients in 4+ star recipes | `analytics_summary.json` |
| 8 | **Top Rated Recipes** | Top 10 by average rating | `top_rated_recipes.csv` |
| 9 | **Steps Distribution** | Statistical summary | `analytics_summary.json` |
| 10 | **Most Commented Recipes** | Top 10 by cooknote count | `analytics_summary.json` |
| 11 | **Longest Recipes** | Top 10 by total time | `analytics_summary.json` |

### 6.2 Generated Visualizations
<img width="350" alt="difficulty_donut_chart" src="https://github.com/user-attachments/assets/e902b7fd-b27f-4c5d-ae28-a53ae87e739d" />

<img width="450" alt="top_ingredients_bar_chart" src="https://github.com/user-attachments/assets/f1b151b2-8130-47f9-9751-05a2d018af97" />

<img width="450" alt="prep_vs_rating_scatter_plot" src="https://github.com/user-attachments/assets/d625182e-a58a-4a24-a626-40f80a6dc108" />

<img width="450" alt="cook_time_histogram" src="https://github.com/user-attachments/assets/ac0c77cc-1ee9-4b69-b749-0fa067e35890" />




| Chart | Type | Description |
|-------|------|-------------|
| `difficulty_donut_chart.png` | 🍩 Donut | Recipe distribution by difficulty |
| `top_ingredients_bar_chart.png` | 📊 Horizontal Bar | Top 20 most used ingredients |
| `prep_vs_rating_scatter_plot.png` | 📈 Scatter | Correlation between prep time and rating |
| `cook_time_histogram.png` | 📉 Histogram | Distribution of cooking times |

### 6.3 Sample Analytics Output

```json
{
  "most_common_ingredients": {
    "Curry Leaves": 18,
    "Peanuts": 16,
    "Goda Masala": 15,
    "Grated Coconut": 14,
    "Green Chilies": 13
  },
  "avg_prep_time": 27.5,
  "avg_cook_time": 38.2,
  "difficulty_distribution": {
    "Easy": 7,
    "Medium": 9,
    "Hard": 5
  },
  "prep_vs_rating_corr": 0.15,
  "top_rated_recipes": [
    {"recipe_id": "xxx", "title": "Puran Poli", "rating": 5.0},
    {"recipe_id": "yyy", "title": "Modak", "rating": 4.8}
  ],
  "ingredients_high_rating": {
    "Jaggery (Gul)": 4.8,
    "Grated Coconut": 4.6,
    "Rice Flour": 4.5
  }
}
```

---

## 7. Known Constraints & Limitations

### 7.1 Firestore Limitations

| Constraint | Impact | Mitigation |
|------------|--------|------------|
| **No native JOINs** | Cannot query across collections | Denormalized data; subcollections used |
| **Read costs** | Each document read is billed | Streaming used instead of batch reads |
| **No aggregations** | No COUNT/SUM/AVG in queries | Aggregations done in Python post-export |
| **Subcollection queries** | Cannot query all subcollections at once | Iterate per parent document |

### 7.2 Pipeline Constraints

| Constraint | Description |
|------------|-------------|
| **Sequential execution** | Steps must run in order (seed → transform → validate → analyze) |
| **Full export required** | No incremental/delta processing |
| **Memory-bound** | All data loaded into pandas DataFrames |
| **Hardcoded paths** | Some scripts use relative paths that assume specific directory |

### 7.3 Data Quality Assumptions

| Assumption | If Violated |
|------------|-------------|
| Difficulty ∈ {Easy, Medium, Hard, Expert} | Marked as invalid |
| Rating ∈ [0, 5] | Marked as invalid |
| Prep + Cook ≤ Total time | Marked as invalid |
| Quantity > 0 | Marked as invalid |

### 7.4 Scalability Notes

- **Current tested capacity:** ~20 recipes, ~200 interactions
- **For larger datasets:** Consider chunked processing or Apache Spark
- **Recommendation:** For 1000+ recipes, implement pagination in export

---

## 8. Deliverables

| Deliverable | Status | Location |
|-------------|--------|----------|
| ✅ Source files for ETL scripts | Complete | `transform_data/transform.py`, `Firebase_Setup/` |
| ✅ Validation script | Complete | `data_validation/validator.py` |
| ✅ Normalized CSV output | Complete | `transform_data/*.csv` |
| ✅ Analytics summary | Complete | `analytics/analytics_summary.json` |
| ✅ README with implementation details | Complete | `README.md` |
| ✅ Visualization charts | Complete | `analytics/charts/*.png` |

---

## 🛠 Tech Stack

| Component | Technology |
|-----------|------------|
| Database | Firebase Firestore |
| Language | Python 3.8+ |
| Data Processing | Pandas, NumPy |
| Visualization | Matplotlib |
| Firebase SDK | firebase-admin |

---

## 📝 License

MIT License - See LICENSE file for details.

---

## 👤 Author

**Dnyaneshwar Potdar**  
Project Link: [GitHub Repository](https://github.com/dnyanesh182/recipe-analytics)
