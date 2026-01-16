import pandas as pd
import random
from pathlib import Path

# ================= CONFIG ================= #

OUTPUT_FILE = "expense_dataset_100k.csv"
TOTAL_ROWS = 100_000
RANDOM_SEED = 42

random.seed(RANDOM_SEED)

# ================= CATEGORY TEMPLATES ================= #

CATEGORY_TEMPLATES = {
    "Food": [
        "pizza", "burger", "restaurant meal", "lunch", "dinner",
        "snacks", "street food", "food delivery", "swiggy order",
        "zomato order", "coffee", "tea", "breakfast"
    ],
    "Groceries": [
        "grocery shopping", "vegetable market", "supermarket",
        "milk purchase", "ration store", "daily groceries"
    ],
    "Shopping": [
        "shopping", "clothes purchase", "online shopping",
        "amazon order", "flipkart order", "new shoes",
        "electronics purchase", "mall shopping"
    ],
    "Entertainment": [
        "movie ticket", "cinema", "netflix subscription",
        "spotify premium", "concert ticket", "game purchase"
    ],
    "Transport": [
        "petrol", "diesel", "fuel refill", "gas station",
        "uber ride", "ola cab", "bus ticket", "train ticket",
        "metro ticket", "taxi fare", "auto rickshaw"
    ],
    "Travel": [
        "flight ticket", "hotel booking", "vacation travel",
        "trip expense", "tour booking", "resort stay"
    ],
    "Utilities": [
        "electricity bill", "water bill", "internet bill",
        "mobile recharge", "wifi payment", "gas bill"
    ],
    "Health": [
        "hospital visit", "medical bill", "doctor consultation",
        "medicine purchase", "pharmacy", "health checkup"
    ],
    "Income": [
        "salary credited", "freelance payment", "bonus received",
        "interest income", "refund received", "cashback received"
    ]
}

# ================= DATA GENERATION ================= #

def generate_dataset():
    rows = []
    categories = list(CATEGORY_TEMPLATES.keys())
    rows_per_category = TOTAL_ROWS // len(categories)

    for category in categories:
        templates = CATEGORY_TEMPLATES[category]

        for _ in range(rows_per_category):
            description = random.choice(templates)

            # Add realistic noise
            noise = random.choice([
                "",
                "",
                f" {random.randint(50, 5000)}",
                " payment",
                " transaction",
                " expense"
            ])

            rows.append({
                "description": description + noise,
                "category": category
            })

    df = pd.DataFrame(rows)
    df = df.sample(frac=1, random_state=RANDOM_SEED)  # shuffle
    return df

# ================= SAVE CSV ================= #

if __name__ == "__main__":
    print("📊 Generating dataset...")
    df = generate_dataset()

    output_path = Path(OUTPUT_FILE)
    df.to_csv(output_path, index=False)

    print(f"✅ Dataset created: {output_path.resolve()}")
    print(f"📈 Total rows: {len(df)}")
