import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import json
from pathlib import Path

def load_csvs():
    # Prefer the project's `transform_data` folder
    project_root = Path(__file__).resolve().parents[1]
    data_dir = project_root / 'transform_data'

    print(f"Loading CSVs from: {data_dir}")
    try:
        recipes = pd.read_csv(str(data_dir / 'recipes.csv'))
        ingredients = pd.read_csv(str(data_dir / 'ingredients.csv'))
        steps = pd.read_csv(str(data_dir / 'steps.csv'))
        interactions = pd.read_csv(str(data_dir / 'interactions.csv'))
        return recipes, ingredients, steps, interactions
    except FileNotFoundError:
        print(f"Error: Could not find CSV files in {data_dir}. Did you run the ETL pipeline?")
        exit(1)

def insights(recipes, ingredients, steps, interactions):
    out = {}
    
    # 1. Most common ingredients
    out["most_common_ingredients"] = ingredients['name'].value_counts().head(20).to_dict()

    # 2. Average preparation time
    out["avg_prep_time"] = recipes['prep_time_min'].dropna().astype(float).mean()

    # 3. Average cooking time
    out["avg_cook_time"] = recipes['cook_time_min'].dropna().astype(float).mean()

    # 4. Difficulty distribution
    out['difficulty_distribution'] = recipes['difficulty'].value_counts().to_dict()

    # 5. Most interacted recipes
    out['most_interacted'] = interactions['recipe_id'].value_counts().head(20).to_dict()

    # 6. Correlation between prep time and average rating
    interactions['rating'] = pd.to_numeric(interactions['rating'], errors='coerce')
    merged = recipes.merge(interactions.groupby('recipe_id')['rating'].mean().reset_index(), left_on='recipe_id', right_on='recipe_id', how='left')
    out['prep_vs_rating_corr'] = merged['prep_time_min'].astype(float).corr(merged['rating'])

    # 7. Ingredients with high ratings
    ing_ratings = ingredients.merge(interactions[['recipe_id','rating']], on='recipe_id', how='left')
    ing_ratings['rating'] = pd.to_numeric(ing_ratings['rating'], errors='coerce')
    ing_score = ing_ratings.groupby('name')['rating'].mean().dropna().sort_values(ascending=False).head(20)
    out['ingredients_high_rating'] = ing_score.to_dict()

    # 8. Top rated recipes
    top_rated = merged.sort_values('rating', ascending=False).head(10)[['recipe_id','title','rating']]
    out['top_rated_recipes'] = top_rated.to_dict(orient='records')

    # 9. Steps count distribution
    steps_count = steps.groupby('recipe_id').size().rename('steps_count')
    out['steps_count_distribution'] = steps_count.describe().to_dict()

    # 10. Recipes with most comments
    comments = interactions[interactions['cooknote'].notnull() & (interactions['cooknote'].str.strip() != '')]
    out['recipes_most_comments'] = comments['recipe_id'].value_counts().head(10).to_dict()

    # 11. Longest total time recipes
    out['longest_total_time'] = recipes[['recipe_id','title','total_time_min']].sort_values('total_time_min', ascending=False).head(10).to_dict(orient='records')

    # Save CSV outputs to current directory
    pd.Series(out['most_common_ingredients']).to_csv('most_common_ingredients.csv')
    pd.DataFrame(out['top_rated_recipes']).to_csv('top_rated_recipes.csv', index=False)

    # Save summary JSON to current directory
    with open('analytics_summary.json', 'w', encoding='utf-8') as f:
        json.dump(out, f, indent=2, default=str)

    return out, merged

def generate_charts(recipes, ingredients, interactions, merged_data, out):
    print("Generating charts...")
    # Create charts directory in current folder
    charts_dir = 'charts'
    os.makedirs(charts_dir, exist_ok=True)

    # Chart 1: Difficulty Distribution (DONUT CHART)
    plt.figure(figsize=(8, 8))
    counts = recipes['difficulty'].value_counts()
    plt.pie(counts, labels=counts.index, autopct='%1.1f%%', startangle=90, pctdistance=0.85, colors=['#66b3ff','#99ff99','#ffcc99'])
    # Draw white circle for Donut effect
    centre_circle = plt.Circle((0,0),0.70,fc='white')
    fig = plt.gcf()
    fig.gca().add_artist(centre_circle)
    plt.title('Recipe Difficulty Breakdown')
    plt.tight_layout()
    plt.savefig(f'{charts_dir}/difficulty_donut_chart.png')
    plt.close() 

    # Chart 2: Top Ingredients (HORIZONTAL BAR CHART)
    plt.figure(figsize=(10, 8))
    top_ing = pd.Series(out['most_common_ingredients'])
    top_ing.sort_values().plot(kind='barh', color='#ff9999', edgecolor='grey')
    plt.title('Top 20 Most Common Ingredients')
    plt.xlabel('Frequency')
    plt.tight_layout()
    plt.savefig(f'{charts_dir}/top_ingredients_bar_chart.png')
    plt.close()

    # Chart 3: Prep Time vs Rating (SCATTER PLOT)
    plt.figure(figsize=(10, 6))
    plt.scatter(merged_data['prep_time_min'], merged_data['rating'], alpha=0.6, c='teal', edgecolors='w', s=80)
    plt.title('Correlation: Prep Time vs Average Rating')
    plt.xlabel('Prep Time (minutes)')
    plt.ylabel('Average Rating (0-5)')
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.savefig(f'{charts_dir}/prep_vs_rating_scatter_plot.png')
    plt.close()

    # Chart 4: Cook Time Distribution (HISTOGRAM)
    plt.figure(figsize=(10, 6))
    plt.hist(recipes['cook_time_min'].dropna(), bins=15, color='#86bf91', edgecolor='black')
    plt.title('Distribution of Cooking Times')
    plt.xlabel('Cooking Time (minutes)')
    plt.ylabel('Number of Recipes')
    plt.grid(axis='y', alpha=0.5)
    plt.tight_layout()
    plt.savefig(f'{charts_dir}/cook_time_histogram.png')
    plt.close()

if __name__ == "__main__":
    recipes, ingredients, steps, interactions = load_csvs()
    # Capture merged_data returned from insights
    out, merged_data = insights(recipes, ingredients, steps, interactions)
    generate_charts(recipes, ingredients, interactions, merged_data, out)
    print(f"Analytics complete. Charts saved to '{os.getcwd()}/charts/'")